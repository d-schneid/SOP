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
        SeleniumTestCase.login(self, "SeleniumTestAdmin", "this_is_a_test")
        self.assertEqual(self.driver.current_url, SeleniumTestCase.BASE_URL)

        self.driver.find_element(By.LINK_TEXT, "Admin").click()
        self.assertEqual(self.driver.current_url, SeleniumTestCase.BASE_URL + "admin/")

        self.driver.find_element(By.LINK_TEXT, "Users").click()
        self.assertEqual(
            SeleniumTestCase.BASE_URL + "admin/authentication/user/",
            self.driver.current_url,
        )

        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.assertEqual(
            SeleniumTestCase.BASE_URL + "admin/authentication/user/add/",
            self.driver.current_url,
        )

        self.driver.find_element(By.ID, "id_username").send_keys(bob_username)
        self.driver.find_element(By.ID, "id_password1").send_keys(bob_password)
        self.driver.find_element(By.ID, "id_password2").send_keys(bob_password)
        self.driver.find_element(By.NAME, "_save").click()
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "admin/authentication/user/[0-9]+/change/",
        )

        # Alice logs herself out
        self.driver.find_element(By.CSS_SELECTOR, "a:nth-child(4)").click()
        self.assertEqual(self.driver.current_url, SeleniumTestCase.BASE_URL + "login/")

        # now Bob can log in
        self.driver.find_element(By.ID, "id_username").send_keys(bob_username)
        self.driver.find_element(By.ID, "id_password").send_keys(bob_password)
        self.driver.find_element(By.ID, "login-button").click()
        self.assertEqual(self.driver.current_url, SeleniumTestCase.BASE_URL)

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
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "experiment/overview/sort-by=[a-zA-Z_]+/",
        )

        self.driver.find_element(By.LINK_TEXT, "Create experiment").click()
        self.assertEqual(
            self.driver.current_url, SeleniumTestCase.BASE_URL + "experiment/create/"
        )

        self.driver.find_element(By.ID, "id_display_name").send_keys(
            "Bobs Erstes Experiment"
        )
        dropdown = self.driver.find_element(By.ID, "id_dataset")
        dropdown.find_element(
            By.XPATH, "//option[. = '" + dataset_name + " | " + bob_username + "']"
        ).click()

        # add algorithms
        self.driver.find_element(
            By.CSS_SELECTOR, "#group_Probabilistic > .flex-grow-1"
        ).click()
        # self.driver.find_element(By.ID, "check-algo-16").click()  # KDE
        self.driver.find_element(
            By.CSS_SELECTOR, "#collapse_Probabilistic .list-group-item:nth-child(5)"
        ).click()
        # TODO

        self.driver.find_element(
            By.CSS_SELECTOR, "#group_Proximity-Based > .flex-grow-1"
        ).click()
        # self.driver.find_element(By.ID, "check-algo-17").click()  # KNN
        self.driver.find_element(
            By.CSS_SELECTOR, "#collapse_Proximity-Based .list-group-item:nth-child(4)"
        ).click()
        # TODO

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "experiment/overview/sort-by=[a-zA-Z_]+/",
        )

        # Bob creates an execution within his new experiment
        self.driver.find_element(By.LINK_TEXT, "New Execution").click()
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "experiment/[0-9]+/execution/create/",
        )

        self.driver.find_element(By.ID, "id_subspace_amount").send_keys("2")
        self.driver.find_element(By.ID, "id_subspaces_min").send_keys("5")
        self.driver.find_element(By.ID, "id_subspaces_max").send_keys("8")
        self.driver.find_element(By.ID, "id_subspace_generation_seed").send_keys("1")

        self.driver.find_element(By.ID, "16_contamination").send_keys("0.2")
        self.driver.find_element(By.ID, "17_contamination").send_keys("0.3")
        self.driver.find_element(By.ID, "17_n_neighbors").send_keys("7")
        self.driver.find_element(By.ID, "17_leaf_size").send_keys("20")

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "experiment/overview/sort-by=[a-zA-Z_]+/",
        )

        # TODO: wait for finish & download result & check
        #  (-> change parameters and dataset)

    def test_user_story_charlie(self):
        # login
        SeleniumTestCase.login(
            self,
            SeleniumTestCase.STANDARD_USERNAME_USER,
            SeleniumTestCase.STANDARD_PASSWORD_USER,
        )
        self.assertEqual(self.driver.current_url, SeleniumTestCase.BASE_URL)

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
        algo_name = "Dr. Metas algorithm"
        algo_description = "Provided by Dr. Meta, for my friend Charlie"
        algo_path = os.path.join("tests", "sample_algorithms", "SampleAlgoKnn.py")
        assert os.path.isfile(algo_path)

        self.driver.find_element(By.LINK_TEXT, "Algorithms").click()
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "algorithm/overview/sort-by=[a-zA-Z_]+/",
        )

        self.driver.find_element(By.LINK_TEXT, "Upload algorithm").click()
        self.assertEqual(
            self.driver.current_url, SeleniumTestCase.BASE_URL + "algorithm/upload/"
        )

        self.driver.find_element(By.ID, "id_display_name").send_keys(algo_name)
        self.driver.find_element(By.ID, "id_description").send_keys(algo_description)
        self.driver.find_element(By.ID, "id_group")
        dropdown = self.driver.find_element(By.ID, "id_group")
        dropdown.find_element(By.XPATH, "//option[. = 'Proximity Based']").click()
        absolute_path = os.path.join(os.getcwd(), algo_path)
        self.driver.find_element(By.ID, "id_path").send_keys(absolute_path)

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "algorithm/overview/sort-by=[a-zA-Z_]+/",
        )

        # create new experiment with own algorithm
        exp_name = "Charlies experiment"

        self.driver.find_element(By.LINK_TEXT, "Experiments").click()
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "experiment/overview/sort-by=[a-zA-Z_]+/",
        )

        self.driver.find_element(By.LINK_TEXT, "Create experiment").click()
        self.assertEqual(
            self.driver.current_url, SeleniumTestCase.BASE_URL + "experiment/create/"
        )

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
        self.driver.find_element(By.ID, "check-algo-3").click()  # own uploaded algo
        # TODO

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "experiment/overview/sort-by=[a-zA-Z_]+/",
        )

        # create new execution
        self.driver.find_element(By.LINK_TEXT, "New Execution").click()
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "experiment/[0-9]+/execution/create/",
        )

        self.driver.find_element(By.ID, "id_subspace_amount").send_keys("2")
        self.driver.find_element(By.ID, "id_subspaces_min").send_keys("5")
        self.driver.find_element(By.ID, "id_subspaces_max").send_keys("8")
        self.driver.find_element(By.ID, "id_subspace_generation_seed").send_keys("1")

        self.driver.find_element(By.ID, "36_contamination").send_keys("0.2")
        self.driver.find_element(By.ID, "36_n_neighbors").send_keys("7")
        self.driver.find_element(By.ID, "36_leaf_size").send_keys("20")

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.assertRegex(
            self.driver.current_url,
            SeleniumTestCase.BASE_URL + "experiment/overview/sort-by=[a-zA-Z_]+/",
        )

        # TODO: wait for finish & download result & check
        #  (-> change parameters and dataset)
