#!/bin/sh

# Unit test and coverage
echo "***** Unit Test *****"
coverage run -m pytest -v -s
echo "***** Coverage tests *****"
coverage report --omit="*/tests/*,*/venv/*" -m ./*.py ./src/*.py

# Coverage report in html
# coverage run -m pytest -v && coverage html --omit="*/test/*,*/venv/*"

# With param -s for input
# coverage run -m pytest - v -s && coverage html --omit="*/test/*,*/venv/*"

# Linter checks
# stop the build if there are Python syntax errors or undefined names
echo "***** Linter: Checking Python syntax errors *****"
flake8 main.py ./src/* --count --select=E9,F63,F7,F82 --show-source --statistics
# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
echo "***** Linter: Checking Python syntax patterns *****"
flake8 main.py ./src/* --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics