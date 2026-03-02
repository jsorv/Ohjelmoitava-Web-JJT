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

Configure the tests folder with vscode Testing, and run them from the Testing tab.

**Main Errors Discussion**
Writing tests helped to spot errors. With location, errors consisted mostly of wrongly implemented imports / circular imports.

With forecasts there was a struggle with the datetime formats that was detected with the functional testing. At first the location parameter was missing from all the WeatherForecastItem methods. 