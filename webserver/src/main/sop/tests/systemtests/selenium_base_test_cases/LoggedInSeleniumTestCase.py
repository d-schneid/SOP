from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase
from tests.systemtests.selenium_base_test_cases.SeleniumUser import SeleniumUser


class LoggedInSeleniumTestCase(SeleniumTestCase):
    user: SeleniumUser

    def setUp(self) -> None:
        super().setUp()

        self.user = SeleniumUser(
            self,
            name=SeleniumTestCase.STANDARD_USERNAME_USER,
            password=SeleniumTestCase.STANDARD_PASSWORD_USER,
        )
        self.user.login()

    def tearDown(self) -> None:
        self.user.logout()

        super().tearDown()
