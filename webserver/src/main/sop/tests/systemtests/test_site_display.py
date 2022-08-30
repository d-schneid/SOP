from unittest import skip

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


@skip
class TestSiteDisplay(StaticLiveServerTestCase):
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
