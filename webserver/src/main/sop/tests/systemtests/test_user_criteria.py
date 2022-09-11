import unittest

from tests.systemtests.selenium_base_test_cases.SeleniumAdmin import SeleniumAdmin
from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase
from tests.systemtests.selenium_base_test_cases.SeleniumUser import SeleniumUser


class TestUserCriteria(SeleniumTestCase):
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

    def test_login_success(self):
        user = SeleniumUser(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_USER,
            password=SeleniumTestCase.STANDARD_PASSWORD_USER,
        )
        user.login()

    @unittest.expectedFailure
    def test_login_failure(self):
        user = SeleniumUser(tc=self, name="does not exist", password="123")
        user.login()

    def test_logout(self):
        user = SeleniumUser(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_USER,
            password=SeleniumTestCase.STANDARD_PASSWORD_USER,
        )
        user.login()

        self.assertTrue(user.logout())

    def test_create_user_success(self):
        new_user = SeleniumUser(
            tc=self,
            name="new_username",
            password="secure123",
        )

        user_admin = SeleniumAdmin(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_ADMIN,
            password=SeleniumTestCase.STANDARD_PASSWORD_ADMIN,
        )
        user_admin.login()

        user_admin.create_user(new_user)

    @unittest.expectedFailure
    def test_create_user_failure(self):
        new_user = SeleniumUser(
            tc=self,
            name="new      username",
            password="",
        )

        user_admin = SeleniumAdmin(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_ADMIN,
            password=SeleniumTestCase.STANDARD_PASSWORD_ADMIN,
        )
        user_admin.login()

        user_admin.create_user(new_user)

    def test_delete_user(self):
        user = SeleniumUser(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_USER,
            password=SeleniumTestCase.STANDARD_PASSWORD_USER,
        )

        user_admin = SeleniumAdmin(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_ADMIN,
            password=SeleniumTestCase.STANDARD_PASSWORD_ADMIN,
        )
        user_admin.login()

        user_admin.delete_user(user)

    def test_promote_denote_admin(self):
        user = SeleniumUser(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_USER,
            password=SeleniumTestCase.STANDARD_PASSWORD_USER,
        )

        user_admin = SeleniumAdmin(
            tc=self,
            name=SeleniumTestCase.STANDARD_USERNAME_ADMIN,
            password=SeleniumTestCase.STANDARD_PASSWORD_ADMIN,
        )
        user_admin.login()

        user_admin.promote_admin(user)
        user_admin.denote_admin(user)

    def test_user_overview(self):
        pass  # TODO: implement
