# API TESTS

This is the testmodule for the APIs functional tests

**Dependencies**

    flask
    flask-restful
    flask-sqlalchemy
    jsonschema
    SQLAlchemy
    pytest
    pytest-cov (for test coverage)

**Instructions**

Install dependencies from repo root:

``` pip intall -r tests/requirements.txt ```

Configure the tests folder with vscode Testing, and run them from the Testing tab.

or 

Run from the command line:

``` pytest tests/test_forecast.py tests/test_location.py tests/test_report.py ```

Additionally you can run tests with test coverage with:

``` pytest --cov=API/src/weatherradar tests/test_forecast.py tests/test_location.py tests/test_report.py ```

**Main Errors Discussion**
Writing tests helped to spot errors. With location, errors consisted mostly of wrongly implemented imports / circular imports.

With forecasts there was a struggle with the datetime formats that was detected with the functional testing. At first the location parameter was missing from all the WeatherForecastItem methods. 