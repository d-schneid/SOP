#!/bin/bash

# install the required algorithms for pyod and for testing with Selenium
pip install -r requirements_pyod_algorithms.txt
pip install -r requirements_test.txt

# install the browsers needed for testing with selenium
# (apt update && upgrade should be run beforehand)

# Preparations: update the system before
sudo apt-get update --quiet
sudo apt-get upgrade --quiet --assume-yes

# Firefox-Browser Installation
sudo apt-get install --install-suggests --quite --assume-yes firefox

# Chrome-Browser Installation
wget -O chrome_browser.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install --install-suggests --quiet --assume-yes ./chrome_browser.deb
rm chrome_browser.deb
