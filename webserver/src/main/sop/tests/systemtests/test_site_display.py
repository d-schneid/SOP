from unittest import skip

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager



class TestSiteDisplay(StaticLiveServerTestCase):
    @skip
    def test_driver_manager_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.headless = True

        service = ChromeService(executable_path=ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=chrome_options)

        # ATTENTION: Webserver has to run locally

        driver.get(self.live_server_url)

        self.assertEqual(driver.title, "Login")
        self.assertIn("Login", driver.page_source)

        driver.quit()

        print("Chrome successful!")

    @skip
    def test_driver_manager_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")

        service = FirefoxService(executable_path=GeckoDriverManager().install())

        driver = webdriver.Firefox(service=service, options=firefox_options)

        driver.get(self.live_server_url)

        self.assertEqual(driver.title, "Login")
        self.assertIn("Login", driver.page_source)

        driver.quit()

        print("Firefox successful!")

    def test_ci_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=2560,1440")
        chrome_options.add_argument("--start-maximized")

        chrome_driver = webdriver.Remote(
            command_executor="http://chrome:4444/wd/hub",
            options=chrome_options,
        )

        chrome_driver.get(self.live_server_url)

        print("Test CI Chrome worked so far!\n----------")
        print("Page source: " + chrome_driver.page_source)
        print("----------------")

        self.assertEqual(chrome_driver.title, "Login")
        self.assertIn("Login", chrome_driver.page_source)

        print("TEST CI CHROME WORKED !!!")

    def test_ci_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--window-size=2560,1440")
        firefox_options.add_argument("--start-maximized")

        firefox_driver = webdriver.Remote(
            command_executor="http://firefox:4444/wd/hub",
            options=firefox_options,
        )

        firefox_driver.get(self.live_server_url)

        print("Test CI Firefox worked so far!\n----------")
        print("Page source: " + firefox_driver.page_source)
        print("----------------")

        self.assertEqual(firefox_driver.title, "Login")
        self.assertIn("Login", firefox_driver.page_source)

        print("TEST CI FIREFOX WORKED !!!")
