from selenium.webdriver.common.by import By

from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase
from tests.systemtests.selenium_base_test_cases.SeleniumUser import SeleniumUser


class SeleniumAdmin(SeleniumUser):
    def __init__(self, tc: SeleniumTestCase, name: str, password: str):
        super().__init__(tc, name, password)
        self._is_admin = True

    def create_user(self, user: SeleniumUser):

        self._create_standard_user(user)

        # promote admin if user is admin
        if user.is_admin:
            self.promote_admin(user)

    def promote_admin(self, user: SeleniumUser):
        pass  # TODO implement

    def denote_admin(self, user: SeleniumUser):
        pass  # TODO implement

    def delete_user(self, user):
        self._navigate_to_admin_screen()

        # TODO implement

        self._navigate_to_home_screen()

        # TODO check in the db

    def _navigate_to_admin_screen(self):
        self._tc.driver.find_element(By.LINK_TEXT, "Admin").click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.ADMIN_BASE)

    def _navigate_to_home_screen(self):
        self._tc.driver.find_element(
            By.XPATH, "//a[contains(text(),'View site')]"
        ).click()
        self._tc.assertUrlMatches(SeleniumTestCase.UrlsSuffixRegex.HOMEPAGE)

    def _create_standard_user(self, user):
        self._navigate_to_admin_screen()

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

        self._navigate_to_home_screen()

        # TODO: assert the user is in the db correctly
