from selenium.webdriver.common.by import By

from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase
from tests.systemtests.selenium_base_test_cases.SeleniumUser import SeleniumUser


class SeleniumAdmin(SeleniumUser):
    def __init__(self, tc: SeleniumTestCase, name: str, password: str):
        super().__init__(tc, name, password)
        self._is_admin = True

    def create_user(self, user: SeleniumUser):
        self._tc.driver.find_element(By.LINK_TEXT, "Admin").click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ADMIN_BASE)

        self._tc.driver.find_element(By.LINK_TEXT, "Users").click()
        self._tc.assertUrlMatches(
            SeleniumTestCase.UrlsSuffixRegex.ADMIN_AUTHENTICATION_USER
        )

        self._tc.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self._tc.assertUrlMatches(
            SeleniumTestCase.UrlsSuffixRegex.ADMIN_AUTHENTICATION_USER_ADD
        )

        self._tc.driver.find_element(By.ID, "id_username").send_keys(user.name)
        self._tc.driver.find_element(By.ID, "id_password1").send_keys(user.password)
        self._tc.driver.find_element(By.ID, "id_password2").send_keys(user.password)
        self._tc.driver.find_element(By.NAME, "_save").click()
        self._tc.assertUrlMatches(
            SeleniumTestCase.UrlsSuffixRegex.ADMIN_AUTHENTICATION_USER_CHANGE
        )

        # TODO: make it possible for admins to also be craeted

        # Alice logs herself out
        self._tc.driver.find_element(By.CSS_SELECTOR, "a:nth-child(4)").click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.LOGIN)
