from django.test import Client, TestCase


class SiteTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_sites_algorithm(self):
        response = self.client.get("/algorithm/overview/", follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/algorithm/", follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/algorithm/overview/sort-by=name/", follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/algorithm/overview/sort-by=group/", follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/algorithm/overview/sort-by=upload_date/", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_sites_datasets(self):
        response = self.client.get("/dataset/", follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/dataset/overview/", follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/dataset/overview/sort-by=name/", follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/dataset/overview/sort-by=upload_date/", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_sites_experiments(self):
        response = self.client.get("/experiment/", follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/experiment/overview/", follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/experiment/overview/sort-by=name/", follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/experiment/overview/sort-by=creation_date/", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_sites_authentication(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/logout/", follow=True)
        self.assertEqual(response.status_code, 200)
