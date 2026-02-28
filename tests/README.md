# API TESTS

This is the testmodule for the APIs functional tests

**Dependencies**

    flask
    flask-restful
    flask-sqlalchemy
    jsonschema
    SQLAlchemy

**Instructions**

Run tests with vscode testing?? 

**Main Errors Discussion**

With forecasts there was a struggle with the datetime formats that was detected with the functional testing. At first the location parameter was missing from all the WeatherForecastItem methods. 