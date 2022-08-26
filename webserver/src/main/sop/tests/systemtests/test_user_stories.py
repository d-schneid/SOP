import datetime
import os
from time import sleep

from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase

from selenium.webdriver.common.by import By


class UserStoriesTest(SeleniumTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_user_story_bob(self):
        # credentials for Bob
        bob_username = "bob"
        bob_password = "this_is_the_secure_password_of_bob"

        # Alice (= Admin) creates a user account for Bob
        self.login(
            SeleniumTestCase.STANDARD_USERNAME_ADMIN,
            SeleniumTestCase.STANDARD_PASSWORD_ADMIN,
        )

        self.driver.find_element(By.LINK_TEXT, "Admin").click()
        self.assertUrlMatches(
            SeleniumTestCase.UrlsSuffixRegex.ADMIN_BASE
        )

        self.driver.find_element(By.LINK_TEXT, "Users").click()
        self.assertUrlMatches(
            SeleniumTestCase.UrlsSuffixRegex.ADMIN_AUTHENTICATION_USER
        )

        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.assertUrlMatches(
            SeleniumTestCase.UrlsSuffixRegex.ADMIN_AUTHENTICATION_USER_ADD
        )

        self.driver.find_element(By.ID, "id_username").send_keys(bob_username)
        self.driver.find_element(By.ID, "id_password1").send_keys(bob_password)
        self.driver.find_element(By.ID, "id_password2").send_keys(bob_password)
        self.driver.find_element(By.NAME, "_save").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ADMIN_AUTHENTICATION_USER_CHANGE)

        # Alice logs herself out
        self.driver.find_element(By.CSS_SELECTOR, "a:nth-child(4)").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.LOGIN)

        # now Bob can log in
        self.login(bob_username, bob_password)

        # Bob uploads his dataset
        valid_dataset_path = os.path.join("tests", "sample_datasets", "canada.csv")
        dataset_name = "Bobs Canada Dataset"
        dataset_description = (
            "This is the Canada Dataset, which Bob uses for testint SOP."
        )

        self.upload_dataset(valid_dataset_path, dataset_name, dataset_description)

        # wait for the dataset to be cleaned
        sleep(5)  # TODO: extract the status (s. sankasten für prototyp)

        # Bob creates an Experiment with his new Dataset
        self.driver.find_element(By.LINK_TEXT, "Experiments").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_OVERVIEW)

        self.driver.find_element(By.LINK_TEXT, "Create experiment").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_CREATE)

        self.driver.find_element(By.ID, "id_display_name").send_keys(
            "Bobs Erstes Experiment"
        )
        dropdown = self.driver.find_element(By.ID, "id_dataset")
        dropdown.find_element(
            By.XPATH, "//option[. = '" + dataset_name + " | " + bob_username + "']"
        ).click()

        # add algorithms
        algo_name_kde = "[PYOD] KDE"
        algo_name_knn = "[PYOD] KNN"

        self.driver.find_element(
            By.CSS_SELECTOR, "#group_Probabilistic > .flex-grow-1"
        ).click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#group_Proximity-Based > .flex-grow-1"
        ).click()

        sleep(0.5)  # TODO: wait for unfolding of groups

        for algo in self.driver.find_elements(By.NAME, "check-algo"):
            if algo.accessible_name in [algo_name_kde, algo_name_knn]:
                algo.click()

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_OVERVIEW)

        # Bob creates an execution within his new experiment
        self.driver.find_element(By.LINK_TEXT, "New Execution").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXECUTION_CREATE)

        # add subspace options
        self.driver.find_element(By.ID, "id_subspace_amount").send_keys("2")
        self.driver.find_element(By.ID, "id_subspaces_min").send_keys("5")
        self.driver.find_element(By.ID, "id_subspaces_max").send_keys("8")
        self.driver.find_element(By.ID, "id_subspace_generation_seed").send_keys("1")

        # change algorithm parameters
        all_labels_kde = self.driver.find_elements(
            By.XPATH,
            "//div[text() = '"
            + algo_name_kde
            + "']/parent::*/parent::*/descendant::label",
        )
        all_labels_knn = self.driver.find_elements(
            By.XPATH,
            "//div[text() = '"
            + algo_name_knn
            + "']/parent::*/parent::*/descendant::label",
        )

        # kde options
        for label in all_labels_kde:
            if "contamination =" == label.text:
                input_element = self.driver.find_element(
                    By.ID, label.get_dom_attribute("for")
                )
                input_element.clear()
                input_element.send_keys("0.2")
            elif "leaf_size =" == label.text:
                input_element = self.driver.find_element(
                    By.ID, label.get_dom_attribute("for")
                )
                input_element.clear()
                input_element.send_keys("10")

        # knn options
        for label in all_labels_knn:
            if "contamination =" == label.text:
                input_element = self.driver.find_element(
                    By.ID, label.get_dom_attribute("for")
                )
                input_element.clear()
                input_element.send_keys("0.3")
            elif "n_neighbors =" == label.text:
                input_element = self.driver.find_element(
                    By.ID, label.get_dom_attribute("for")
                )
                input_element.clear()
                input_element.send_keys("3")
            elif "leaf_size =" == label.text:
                input_element = self.driver.find_element(
                    By.ID, label.get_dom_attribute("for")
                )
                input_element.clear()
                input_element.send_keys("20")

        self.driver.find_element(By.XPATH, "//input[@type='submit']").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_OVERVIEW)

        # TODO: wait for finish & download result & check
        #  (-> change parameters and dataset)

    def test_user_story_charlie(self):
        # login
        self.login(
            SeleniumTestCase.STANDARD_USERNAME_USER,
            SeleniumTestCase.STANDARD_PASSWORD_USER,
        )

        # upload own dataset
        valid_dataset_path = os.path.join("tests", "sample_datasets", "canada.csv")
        dataset_name = "Charlies Canada Dataset"
        dataset_description = (
            "This is the Canada Dataset, which Chralie uses for testint SOP."
        )

        self.upload_dataset(valid_dataset_path, dataset_name, dataset_description)

        # wait for the dataset to be cleaned
        sleep(5)  # TODO: extract the status (s. sankasten für prototyp)

        # upload own algorithm
        #  generate a unique name
        algo_name = "Dr. Metas algorithm - " + str(datetime.datetime.now())
        algo_description = "Provided by Dr. Meta, for my friend Charlie"
        algo_path = os.path.join("tests", "sample_algorithms", "SampleAlgoKnn.py")
        assert os.path.isfile(algo_path)

        self.driver.find_element(By.LINK_TEXT, "Algorithms").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ALGORITHM_OVERVIEW)

        self.driver.find_element(By.LINK_TEXT, "Upload algorithm").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ALGORITHM_UPLOAD)

        self.driver.find_element(By.ID, "id_display_name").send_keys(algo_name)
        self.driver.find_element(By.ID, "id_description").send_keys(algo_description)
        self.driver.find_element(By.ID, "id_group")
        dropdown = self.driver.find_element(By.ID, "id_group")
        dropdown.find_element(By.XPATH, "//option[. = 'Proximity Based']").click()
        absolute_path = os.path.join(os.getcwd(), algo_path)
        self.driver.find_element(By.ID, "id_path").send_keys(absolute_path)

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ALGORITHM_OVERVIEW)

        # wait for algorithm to be checked
        sleep(5)  # TODO: extract the status

        # create new experiment with own algorithm
        exp_name = "Charlies experiment"

        self.driver.find_element(By.LINK_TEXT, "Experiments").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_OVERVIEW)

        self.driver.find_element(By.LINK_TEXT, "Create experiment").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_CREATE)

        self.driver.find_element(By.ID, "id_display_name").send_keys(exp_name)
        dropdown = self.driver.find_element(By.ID, "id_dataset")
        dropdown.find_element(
            By.XPATH,
            "//option[. = '"
            + dataset_name
            + " | "
            + SeleniumTestCase.STANDARD_USERNAME_USER
            + "']",
        ).click()

        # add own algorithm
        self.driver.find_element(
            By.CSS_SELECTOR, "#group_Proximity-Based > .flex-grow-1"
        ).click()

        sleep(0.5)  # TODO: wait for unfolding of group

        for algo in self.driver.find_elements(By.NAME, "check-algo"):
            if algo.accessible_name == algo_name:
                algo.click()
                break

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_OVERVIEW)

        # create new execution
        self.driver.find_element(By.LINK_TEXT, "New Execution").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXECUTION_CREATE)

        # enter subspace data
        self.driver.find_element(By.ID, "id_subspace_amount").send_keys("2")
        self.driver.find_element(By.ID, "id_subspaces_min").send_keys("5")
        self.driver.find_element(By.ID, "id_subspaces_max").send_keys("8")
        self.driver.find_element(By.ID, "id_subspace_generation_seed").send_keys("1")

        # change option for the specific algorithm
        all_labels = self.driver.find_elements(
            By.XPATH,
            "//div[text() = '" + algo_name + "']/parent::*/parent::*/descendant::label",
        )

        for label in all_labels:
            if "contamination =" == label.text:
                input_element = self.driver.find_element(
                    By.ID, label.get_dom_attribute("for")
                )
                input_element.clear()
                input_element.send_keys("0.2")
            elif "n_neighbors =" == label.text:
                input_element = self.driver.find_element(
                    By.ID, label.get_dom_attribute("for")
                )
                input_element.clear()
                input_element.send_keys("7")
            elif "leaf_size =" == label.text:
                input_element = self.driver.find_element(
                    By.ID, label.get_dom_attribute("for")
                )
                input_element.clear()
                input_element.send_keys("20")

        self.driver.find_element(By.XPATH, "//input[@type='submit']").click()
        self.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.EXPERIMENT_OVERVIEW)

        # TODO: wait for finish & download result & check
        #  (-> change parameters and dataset)
