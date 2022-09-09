<div align="center">
<img src="./static/assets/logo_app.png" alt="drawing" width="400"/>
<a href="https://richionline-portfolio.nw.r.appspot.com"><img src="https://falken-home.herokuapp.com/static/home_project/img/falken_logo.png" width=50 alt="Personal Portfolio web"></a>

![Version](https://img.shields.io/badge/version-1.0.0-blue) ![GitHub language count](https://img.shields.io/github/languages/count/falken20/parrao_weather_web) ![GitHub Top languaje](https://img.shields.io/github/languages/top/falken20/parrao_weather_web) ![Test coverage](https://img.shields.io/badge/test%20coverage-0%25-green) ![GitHub License](https://img.shields.io/github/license/falken20/search_extensions)


[![Richi web](https://img.shields.io/badge/web-richionline-blue)](https://richionline-portfolio.nw.r.appspot.com) [![Twitter](https://img.shields.io/twitter/follow/richionline?style=social)](https://twitter.com/richionline)

</div>



Web to get the summary data from the personal weather station

---
##### Endpoint
https://richionline-portfolio.nw.r.appspot.com

##### Deploy in Google Cloud Platform

```
gcloud app deploy
```

##### Setup

```bash
pip install -r requirements.txt
```

##### Running the app

```bash
flask run (with .flaskenv)
```
or
```
flask run -app PATH_APP
```

##### Setup tests

```bash
pip install -r requirements-tests.txt
```

##### Running the tests with pytest and coverage

```bash
./scripts/check_project.sh
```
or
```bash
coverage run -m pytest -v && coverage html --omit=*/venv/*,*/tests/*
```
---

##### Doc API wunderground.com

API General doc: https://docs.google.com/document/d/1eKCnKXI9xnoMGRRzOL1xPCBihNV2rOet08qpE_gArAY/edit
API Current conditions: https://ibm.co/v2PWSCC

##### Icons used
https://icons8.com/

##### Versions

1.0.0 First version