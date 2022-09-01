from __future__ import annotations

import copy
import os
import unittest
from typing import Union
from bs4 import BeautifulSoup

import selenium
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from authentication.models import User
from experiments.management.commands import pyodtodb
from tests.systemtests.selenium_base_test_cases.SeleniumTestCase import SeleniumTestCase


# ----------- Extracting Data -----------


def get_dataset_div(page_source: WebElement, dataset_name: str) -> WebElement:
    return page_source.find_element(
        By.XPATH,
        "//a[normalize-space(text()) = '"
        + dataset_name
        + "']/parent::*/following-sibling::a",
    )


# --------- Setting Up / Tearing Down the Test Environment ----------


def add_pyod_algos_to_db():
    # add a new attribute, which is a deepcopy of the attribute PYOD_ALGORITHMS
    # so the original values are saved
    # (and the original attribute can be reset, s. below)
    # as the renaming will not work otherwise (after the first time)
    setattr(pyodtodb, "ORG_PYOD_DATA", copy.deepcopy(pyodtodb.PYOD_ALGORITHMS))

    pyodtodb.Command().handle()

    # reset the original attribute
    pyodtodb.PYOD_ALGORITHMS = pyodtodb.ORG_PYOD_DATA


def add_users_to_db():
    #  generate a unique username
    SeleniumTestCase.STANDARD_USERNAME_USER = SeleniumTestCase._BASE_USERNAME_USER
    SeleniumTestCase.STANDARD_USERNAME_ADMIN = SeleniumTestCase._BASE_USERNAME_ADMIN
    assert not User.objects.filter(
        username=SeleniumTestCase.STANDARD_USERNAME_USER
    ).exists()
    assert not User.objects.filter(
        username=SeleniumTestCase.STANDARD_USERNAME_ADMIN
    ).exists()

    # set passwords
    SeleniumTestCase.STANDARD_PASSWORD_USER = SeleniumTestCase._BASE_PASSWORD
    SeleniumTestCase.STANDARD_PASSWORD_ADMIN = SeleniumTestCase._BASE_PASSWORD

    #  add them
    User.objects.create_user(
        username=SeleniumTestCase.STANDARD_USERNAME_USER,
        password=SeleniumTestCase.STANDARD_PASSWORD_USER,
    )
    user_admin = User.objects.create_user(
        username=SeleniumTestCase.STANDARD_USERNAME_ADMIN,
        password=SeleniumTestCase.STANDARD_PASSWORD_ADMIN,
    )
    user_admin.is_staff = True
    user_admin.is_superuser = True
    user_admin.save()


def initialize_the_webdriver() -> Union[
    selenium.webdriver.Chrome | selenium.webdriver.Firefox
]:

    # read the selenium_browser.conf-file for settings (if available)
    if os.path.isfile(SeleniumTestCase.BROWSER_VALUE_CONF_FILEPATH):
        with open(SeleniumTestCase.BROWSER_VALUE_CONF_FILEPATH, "r") as file:
            browser_var = file.read().strip()
        print("Selenium Config File Found! - Contents: |" + browser_var + "|")
    else:
        print(
            "Selenium Config File NOT Found! - Expected location was: "
            + SeleniumTestCase.BROWSER_VALUE_CONF_FILEPATH
        )
        browser_var = SeleniumTestCase.BROWSER_VALUE_FIREFOX

    # Set up the webdriver (for Chrome or Firefox)
    # (the standard browser used is the Firefox browser)
    if browser_var == SeleniumTestCase.BROWSER_VALUE_CHROME:
        # setup chrome webdriver
        print("Chrome Browser is used for Selenium Test Cases")

        chrome_service = ChromeService(executable_path=ChromeDriverManager().install())

        # add options for the browser
        chrome_options = ChromeOptions()

        if str(os.environ.get("CI")) == "true":
            print("Running in CI - turning off sandbox for Chrome to work")
            chrome_options.add_argument("--no-sandbox")
        else:
            print("Running NOT in CI")

        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=2560,1440")
        chrome_options.add_argument("--start-maximized")

        # create driver object
        driver = selenium.webdriver.Chrome(
            service=chrome_service,
            options=chrome_options,
        )

    else:
        # setup firefox webdriver
        print("Firefox Browser is used for Selenium Test Cases")

        firefox_service = FirefoxService(executable_path=GeckoDriverManager().install())

        # add options for the browser
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--window-size=2560,1440")
        firefox_options.add_argument("--start-maximized")

        # create driver object
        driver = selenium.webdriver.Firefox(
            service=firefox_service, options=firefox_options
        )

    # setting: wait, if an element is not found
    driver.implicitly_wait(30)

    return driver


def save_artefacts_if_failure(
    driver: Union[selenium.webdriver.Chrome | selenium.webdriver.Firefox],
    result: unittest.TestResult,
    test_method_name: str,
):

    # check if an error has occurred
    if result.errors:
        err_type = "ERROR"
    # or a failure
    elif result.failures:
        err_type = "FAILURE"
    else:
        err_type = None

    # if there is and error, take a screenshot and save the page source
    if err_type is not None:
        # screenshot
        screenshot_path = os.path.join(
            SeleniumTestCase.SELENIUM_ERROR_PATH,
            "selenium_screenshot_{err_type}_{method_name}.png",
        ).format(method_name=test_method_name, err_type=err_type)

        driver.save_screenshot(screenshot_path)

        # save page source (original and pretty version)
        page_source_path_base = os.path.join(
            SeleniumTestCase.SELENIUM_ERROR_PATH,
            "selenium_page_source_{err_type}_{method_name}.html",
        ).format(method_name=test_method_name, err_type=err_type)

        base_source_parts = page_source_path_base.split(".")

        # save original
        page_source_path_org = base_source_parts[0] + "_org." + base_source_parts[1]

        with open(page_source_path_org, "w") as file:
            file.write(driver.page_source)

        # save prettified version
        page_source_path_pretty = (
            base_source_parts[0] + "_pretty." + base_source_parts[1]
        )

        pretty_source = BeautifulSoup(driver.page_source, "html.parser").prettify()
        with open(page_source_path_pretty, "w") as file:
            file.write(pretty_source)
