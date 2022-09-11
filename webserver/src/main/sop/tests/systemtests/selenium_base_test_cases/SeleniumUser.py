from selenium.webdriver.common.by import By

from authentication.models import User
from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase


class SeleniumUser:
    def __init__(self, tc: SeleniumTestCase, name: str, password: str):
        self._tc = tc
        self._name = name
        self._password = password
        self._is_admin = False

    def login(self):
        # first try to log out
        self.logout()

        self._tc.driver.find_element(By.LINK_TEXT, "Login").click()
        self._tc.driver.find_element(By.ID, "id_username").send_keys(self._name)
        self._tc.driver.find_element(By.ID, "id_password").send_keys(self._password)
        self._tc.driver.find_element(By.ID, "login-button").click()

        # assert that the login worked
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.HOMEPAGE)

        # check, if links to subpages are in the generated site
        self._tc.assertIn("/experiment/overview", self._tc.driver.page_source)
        self._tc.assertIn("/dataset/overview", self._tc.driver.page_source)
        self._tc.assertIn("/algorithm/overview", self._tc.driver.page_source)

        # logout should be accessible
        self._tc.assertIn("Logout", self._tc.driver.page_source)
        self._tc.assertIn("/logout", self._tc.driver.page_source)

    def logout(self) -> bool:
        if "Logout" in self._tc.driver.page_source:
            self._tc.driver.find_element(By.LINK_TEXT, "Logout").click()
            return True
        else:
            return False

    def get_from_db(self):
        user_list = User.objects.filter(username=self._name)
        self._tc.assertEqual(len(user_list), 1)
        return user_list.first()

    @property
    def name(self):
        return self._name

    @property
    def password(self):
        return self._password

    @property
    def is_admin(self):
        return self._is_admin
