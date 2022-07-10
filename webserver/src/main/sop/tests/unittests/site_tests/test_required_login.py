from django.test import Client, TestCase


class UrlLoginRequiredTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_algorithm_overview_redirect_to_login(self):
        response = self.client.get("/algorithm/overview/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/algorithm/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/algorithm/overview/sort-by=name/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/algorithm/overview/sort-by=group/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/algorithm/overview/sort-by=upload_date/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

    def test_algorithm_upload_redirect_to_login(self):
        response = self.client.get("/algorithm/upload/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

    def test_algorithm_edit_redirect_to_login(self):
        response = self.client.get(f"/algorithm/1/edit/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

    def test_algorithm_delete_redirect_to_login(self):
        response = self.client.get("/algorithm/1/delete/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

    def test_dataset_overview_redirect_to_login(self):
        response = self.client.get("/dataset/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/dataset/overview/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/dataset/overview/sort-by=name/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/dataset/overview/sort-by=upload_date/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

    def test_dataset_upload_redirect_to_login(self):
        response = self.client.get("/dataset/upload/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

    def test_dataset_edit_view_redirect_to_login(self):
        response = self.client.get("/dataset/1/edit/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

    def test_dataset_delete_view_redirect_to_login(self):
        response = self.client.get("/dataset/1/delete/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

    def test_experiment_overview_redirect_to_login(self):
        response = self.client.get("/experiment/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/experiment/overview/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/experiment/overview/sort-by=name/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/experiment/overview/sort-by=creation_date/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

    def test_experiment_create_redirect_to_login(self):
        response = self.client.get("/experiment/create/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("experiment_create.html")

    def test_experiment_edit_view_redirect_to_login(self):
        response = self.client.get("/experiment/1/edit/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

    def test_experiment_delete_view_redirect_to_login(self):
        response = self.client.get("/experiment/1/delete/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

    def test_authentication_redirect_to_login(self):
        response = self.client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("registration/login.html")

        response = self.client.get("/logout/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("registration/login.html")
