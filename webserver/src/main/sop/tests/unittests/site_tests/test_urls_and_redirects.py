from experiments.models import Algorithm, Dataset, Experiment
from tests.unittests.views.LoggedInTestCase import LoggedInTestCase


class LoggedInSiteTests(LoggedInTestCase):
    def test_algorithm_overview_urls_logged_in(self):
        response = self.client.get("/algorithm/overview/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, "algorithm_overview.html")

        response = self.client.get("/algorithm/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, "algorithm_overview.html")

        response = self.client.get("/algorithm/overview/sort-by=name/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_overview.html")

        response = self.client.get("/algorithm/overview/sort-by=group/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_overview.html")

        response = self.client.get("/algorithm/overview/sort-by=upload_date/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_overview.html")

    def test_algorithm_upload_urls_logged_in(self):
        response = self.client.get("/algorithm/upload/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_upload.html")

    def test_algorithm_edit_urls_logged_in(self):
        algo = Algorithm.objects.create(user=self.user)
        response = self.client.get(f"/algorithm/{algo.pk}/edit/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_edit.html")

    def test_dataset_overview_urls_logged_in(self):
        response = self.client.get("/dataset/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, "dataset_overview.html")

        response = self.client.get("/dataset/overview/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, "dataset_overview.html")

        response = self.client.get("/dataset/overview/sort-by=name/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dataset_overview.html")

        response = self.client.get("/dataset/overview/sort-by=upload_date/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dataset_overview.html")

    def test_dataset_upload_urls_logged_in(self):
        response = self.client.get("/dataset/upload/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dataset_upload.html")

    def test_dataset_edit_urls_logged_in(self):
        dataset = Dataset.objects.create(datapoints_total=0, dimensions_total=0, user=self.user)
        response = self.client.get(f"/dataset/{dataset.pk}/edit/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dataset_edit.html")

    def test_experiment_overview_urls_logged_in(self):
        response = self.client.get("/experiment/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(
            response, "experiment_overview.html"
        )

        response = self.client.get("/experiment/overview/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(
            response, "experiment_overview.html"
        )

        response = self.client.get("/experiment/overview/sort-by=name/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "experiment_overview.html"
        )

        response = self.client.get("/experiment/overview/sort-by=creation_date/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "experiment_overview.html"
        )

    def test_experiment_create_urls_logged_in(self):
        response = self.client.get("/experiment/create/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "experiment_create.html"
        )

    def test_experiment_edit_urls_logged_in(self):
        dataset = Dataset.objects.create(datapoints_total=0, dimensions_total=0, user=self.user)
        exp = Experiment.objects.create(dataset=dataset, user=self.user)
        response = self.client.get(f"/experiment/{exp.pk}/edit/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experiment_edit.html")

    def test_authentication_urls_logged_in(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)
