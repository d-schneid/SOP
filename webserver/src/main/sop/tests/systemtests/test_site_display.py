import unittest
from unittest import skip

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


class TestSiteDisplay(unittest.TestCase):
    def test_driver_manager_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.headless = True

        service = ChromeService(executable_path=ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=chrome_options)

        # ATTENTION: Webserver has to run locally

        driver.get("http://127.0.0.1:8000/")

        self.assertEqual(driver.title, "Subspace Outlier Profiling")
        self.assertTrue("Login" in driver.page_source)

        driver.quit()

    def test_driver_manager_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")

        service = FirefoxService(executable_path=GeckoDriverManager().install())

        driver = webdriver.Firefox(service=service, options=firefox_options)

        driver.get("http://127.0.0.1:8000/")

        self.assertEqual(driver.title, "Subspace Outlier Profiling")
        self.assertTrue("Login" in driver.page_source)

        driver.quit()
