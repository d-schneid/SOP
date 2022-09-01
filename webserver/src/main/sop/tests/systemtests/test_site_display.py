import urllib

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


class TestSiteDisplay(StaticLiveServerTestCase):
    def test_driver_manager_chrome(self):
        print("======== CHECKING URL accessible in CHROME driver tests =========")

        page = urllib.request.urlopen(self.live_server_url)
        print("Status: " + str(page.status))
        print("Url: " + str(page.url))
        print("Headers: ------------\n" + str(page.headers) + "\n------------")
        print("Content: -----------\n" + page.read(300).decode("utf-8") + "\n---------")

        print("======= URL check endent ==========")

        print("============ STARTING CHROME driver Setup ============")

        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--window-size=2560,1440")
        chrome_options.add_argument("--start-maximized")

        service = ChromeService(executable_path=ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=chrome_options)

        print("====== START Chrome driver tests ======")

        driver.get(self.live_server_url)

        print("======= Got url - now printing info =======")

        print("Test driver Chrome: " + driver.title)
        print("----------------------\nTest driver Chrome: Page source:------")
        print(driver.page_source[:20] + "\n------------")

        print("Live Server URL: " + self.live_server_url)

        print("====== Info ende - now asserting =======")

        self.assertEqual(driver.title, "Login")
        self.assertIn("Login", driver.page_source)

        driver.quit()

        print("======= Chrome successful! =========")

    def test_driver_manager_firefox(self):
        print("======== CHECKING URL accessible in FIREFOX driver tests =========")

        page = urllib.request.urlopen(self.live_server_url)
        print("Status: " + str(page.status))
        print("Url: " + str(page.url))
        print("Headers: ------------\n" + str(page.headers) + "\n------------")
        print("Content: -----------\n" + page.read(300).decode("utf-8") + "\n---------")

        print("======= URL check endent ==========")

        print("============ STARTING FIREFOX driver Setup ============")

        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--window-size=2560,1440")
        firefox_options.add_argument("--start-maximized")

        service = FirefoxService(executable_path=GeckoDriverManager().install())

        driver = webdriver.Firefox(service=service, options=firefox_options)

        print("====== START Firefox driver tests ======")

        driver.get(self.live_server_url)

        print("======= Got url - now printint info =======")

        print("Test driver Firefox: " + driver.title)
        print("----------------------\nTest driver Firefox: Page source:--------")
        print(driver.page_source[:20] + "\n------------")

        print("Live Server URL: " + self.live_server_url)

        print("====== Info ende - now asserting =======")

        self.assertEqual(driver.title, "Login")
        self.assertIn("Login", driver.page_source)

        driver.quit()

        print("======== Firefox successful! ==========")
