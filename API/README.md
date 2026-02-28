# WeatherRadar API

This is an information storage API for weather station data

**Dependencies**

	- flask
    - flask-restful
    - flask-sqlalchemy
    - jsonschema
    - SQLAlchemy

**Setup framework**

????

**Init and populate database**

(Make sure you have all dependencies)
From repo root run this command:

``` python -m API.src.scripts.populate_db ```

This initializes a few locations and reports to the database.

**How to run this API**

From repo root run this command:

``` flask --app=API.src.weatherradar --debug run ```

**URL to access this API**

The URL to access your API (usually nameofapplication/api/version/)=> the path to your application. We mean the entry point, the main endpoint of your API.

Ei kai meillä tämmöstä ole???

