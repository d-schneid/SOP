import os

from tests.systemtests.selenium_base_test_cases.SeleniumAdmin import SeleniumAdmin
from tests.systemtests.selenium_base_test_cases.SeleniumAlgoGroup import (
    SeleniumAlgoGropu,
)
from tests.systemtests.selenium_base_test_cases.SeleniumAlgorithm import (
    SeleniumAlgorithm,
)
from tests.systemtests.selenium_base_test_cases.SeleniumDataset import SeleniumDataset
from tests.systemtests.selenium_base_test_cases.SeleniumExecution import (
    SeleniumExecution,
)
from tests.systemtests.selenium_base_test_cases.SeleniumExperiment import (
    SeleniumExperiment,
)
from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase
from tests.systemtests.selenium_base_test_cases.SeleniumUser import SeleniumUser


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
        user_bob = SeleniumUser(
            tc=self, name="bob", password="this_is_the_secure_password_of_bob"
        )

        # Alice (= Admin) creates a user account for Bob
        user_admin = SeleniumAdmin(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_ADMIN,
            password=SeleniumTestCase.STANDARD_PASSWORD_ADMIN,
        )
        user_admin.login()

        user_admin.create_user(user_bob)

        # now Bob can log in
        user_bob.login()

        # Bob uploads his dataset
        valid_dataset_path = os.path.join(
            "tests", "sample_datasets", "canada_testing.csv"
        )
        dataset_name = "Bobs Canada Dataset"
        dataset_description = (
            "This is the Canada Dataset, which Bob uses for testint SOP."
        )

        dataset = SeleniumDataset(
            tc=self,
            path=valid_dataset_path,
            name=dataset_name,
            description=dataset_description,
            user=user_bob,
            failure_expected=False,
        )

        dataset.upload()

        # wait for the dataset to be cleaned
        dataset.wait_until_cleaned()

        # Bob creates an Experiment with his new Dataset
        experiment_name = "Bobs Erstes Experiment"
        algo_name_kde = "[PYOD] KDE"
        algo_name_knn = "[PYOD] KNN"

        experiment = SeleniumExperiment(
            tc=self,
            dataset=dataset,
            name=experiment_name,
            list_algo_names=[algo_name_kde, algo_name_knn],
            user=user_bob,
        )

        experiment.create()

        # Bob creates an execution within his new experiment
        execution = SeleniumExecution(
            subspace_amount="2",
            subspaces_min="5",
            subspaces_max="8",
            subspace_gen_seed="1",
            algos=[
                {
                    "key": algo_name_kde,
                    "contamination": "0.2",
                    "leaf_size": "10",
                },
                {
                    "key": algo_name_knn,
                    "contamination": "0.3",
                    "n_neighbors": "3",
                    "leaf_size": "20",
                },
            ],
        )

        experiment.add_execution(execution)

        experiment.wait_until_execution_finished(execution)
        experiment.download_execution_result(execution)

    def test_user_story_charlie(self):
        user_charlie = SeleniumUser(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_USER,
            password=SeleniumTestCase.STANDARD_PASSWORD_USER,
        )
        user_charlie.login()

        # upload own dataset
        dataset = SeleniumDataset(
            tc=self,
            path=os.path.join("tests", "sample_datasets", "canada_testing.csv"),
            name="Charlies Canada Dataset",
            description="This is the Canada Dataset, which Chralie uses for testint SOP.",
            user=user_charlie,
            failure_expected=False,
        )

        dataset.upload()
        dataset.wait_until_cleaned()

        # upload own algorithm
        algorithm = SeleniumAlgorithm(
            tc=self,
            name="Dr. Metas algorithm",
            description="Provided by Dr. Meta, for my friend Charlie",
            group=SeleniumAlgoGropu.PROXIMITY_BASED,
            path=os.path.join("tests", "sample_algorithms", "SampleAlgoKnn.py"),
            user=user_charlie,
        )

        algorithm.upload()

        # create new experiment with own algorithm
        experiment = SeleniumExperiment(
            tc=self,
            name="Charlies experiment",
            dataset=dataset,
            list_algo_names=[algorithm.name],
            user=user_charlie,
        )
        experiment.create()

        # create new execution
        execution = SeleniumExecution(
            subspace_amount="2",
            subspaces_min="5",
            subspaces_max="8",
            subspace_gen_seed="1",
            algos=[
                {
                    "key": algorithm.name,
                    "contamination": "0.2",
                    "n_neighbors": "7",
                    "leaf_size": "20",
                }
            ],
        )
        experiment.add_execution(execution)

        experiment.wait_until_execution_finished(execution)
        experiment.download_execution_result(execution)
