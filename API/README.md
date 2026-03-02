# WeatherRadar API

This is an information storage API for weather station data

**Dependencies**

	- flask
    - flask-restful
    - flask-sqlalchemy
    - jsonschema
    - SQLAlchemy

**Setup framework**

1. ```git clone https://github.com/jsorv/Ohjelmoitava-Web-JJT.git```
2. ``` cd Ohjelmoitava-Web-JJT ```
3. *Create and activate virtual environment*
4. ``` pip install -e API/src ```

**Init and populate database**

From repo root:

``` python -m API.src.scripts.populate_db ```

**How to run this API**

From repo root:

``` flask --app=API.src.weatherradar --debug run ```

**URL to access this API**

weatherradar/api/

