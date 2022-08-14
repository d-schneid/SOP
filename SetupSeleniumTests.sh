#!/bin/bash

# add the required users for Selenium Test cases to the database
python3 webserver/src/main/sop/manage.py createuser --username SeleniumTestUser --password this_is_a_test
python3 webserver/src/main/sop/manage.py createuser --username SeleniumTestAdmin --password this_is_a_test --admin --staff

# add pyod algorithms to db and install the required algorithms
pip install -r requirements_pyod_algorithms.txt
python3 webserver/src/main/sop/manage.py pyodtodb
