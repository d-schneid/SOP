import urllib
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

    def test_driver_manager_chrome(self):

        print("======== CHECKING URL accessible in CHROME driver tests =========")

        page = urllib.request.urlopen(self.live_server_url)
        print("Status: " + str(page.status))
        print("Url: " + str(page.url))
        print("Headers: ------------\n" + str(page.headers) + "\n------------")
        print("Content: -----------\n" + page.read(300).decode("utf-8") + "\n---------")

        print("======= URL check endent ==========")


        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=2560,1440")
        chrome_options.add_argument("--start-maximized")

        service = ChromeService(executable_path=ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=chrome_options)

        print("====== START Chrome driver tests ======")

        driver.get(self.live_server_url)

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


        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--window-size=2560,1440")
        firefox_options.add_argument("--start-maximized")

        service = FirefoxService(executable_path=GeckoDriverManager().install())

        driver = webdriver.Firefox(service=service, options=firefox_options)

        print("====== START Firefox driver tests ======")

        driver.get(self.live_server_url)

        self.assertEqual(driver.title, "Login")
        self.assertIn("Login", driver.page_source)

        driver.quit()

        print("======== Firefox successful! ==========")

    @skip
    def test_ci_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=2560,1440")
        chrome_options.add_argument("--start-maximized")

        chrome_driver = webdriver.Remote(
            command_executor="http://chrome:4444/wd/hub",
            options=chrome_options,
        )

        print("Test CI Chrome: Init worked !\n----------")

        chrome_driver.get("https://de.wikipedia.org/wiki/Lorem_ipsum")

        print("Test CI Chrome: " + chrome_driver.title)
        print("----------------------\nTest CI Chrome: Page source:")
        print(chrome_driver.page_source[:20] + "\n------------")

        print("Live Server URL: " + self.live_server_url)

        print("=================")

        page = urllib.request.urlopen(self.live_server_url)
        print("Status: " + str(page.status))
        print("Url: " + str(page.url))
        print("Headers: ------------\n" + str(page.headers) + "\n------------")
        print("Content: -----------\n" + page.read(300).decode("utf-8") + "\n---------")

        print("========Try to access live_server_url=======")

        chrome_driver.get(self.live_server_url)

        print("Test CI Chrome OWN page request worked!\n----------")
        print("Page source: " + chrome_driver.page_source[:20])
        print("----------------")

        self.assertEqual(chrome_driver.title, "Login")
        self.assertIn("Login", chrome_driver.page_source[:20])

        print("TEST CI CHROME WORKED !!!")

    @skip
    def test_ci_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--window-size=2560,1440")
        firefox_options.add_argument("--start-maximized")
        firefox_options.add_argument("--ignore-ssl-errors=yes")
        firefox_options.add_argument("--ignore-certificate-errors")

        firefox_driver = webdriver.Remote(
            command_executor="http://firefox:4444/wd/hub",
            options=firefox_options,
        )

        print("Test CI Firefox: Init worked !\n----------")

        firefox_driver.get("https://de.wikipedia.org/wiki/Lorem_ipsum")

        print("Test CI Firefox: " + firefox_driver.title)
        print("----------------------\nTest CI Firefox: Page source:")
        print(firefox_driver.page_source[:20] + "\n------------")

        print("Live Server URL: " + self.live_server_url)

        print("=================")

        page = urllib.request.urlopen(self.live_server_url)
        print("Status: " + str(page.status))
        print("Url: " + str(page.url))
        print("Headers: ------------\n" + str(page.headers) + "\n------------")
        print("Content: -----------\n" + page.read(300).decode("utf-8") + "\n---------")

        print("========Try to access live_server_url=======")

        firefox_driver.get(self.live_server_url)

        print("Test CI Firefox OWN page request worked!\n----------")
        print("Page source: " + firefox_driver.page_source[:20])
        print("----------------")

        self.assertEqual(firefox_driver.title, "Login")
        self.assertIn("Login", firefox_driver.page_source[:20])

        print("TEST CI FIREFOX WORKED !!!")
