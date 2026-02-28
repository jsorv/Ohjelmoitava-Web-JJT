from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType, NotFound, Conflict
from jsonschema import validate, ValidationError
import json

from API.src.weatherradar.models import WeatherReport
from API.src.weatherradar import db


class WeatherForecasts(Resource):

    def get(self, location):
        """Get all forecasts for a location."""
        forecasts = WeatherReport.query.filter_by(
            location_id=location.location_id, entry_type="forecast"
        ).all()
        return Response(
            response=json.dumps([f.serialize() for f in forecasts]),
            mimetype="application/json",
            status=200,
        )

    def post(self, location):
        """Create a new forecast for a location."""
        if not request.json:
            raise UnsupportedMediaType(description="Request body must be JSON")

        try:
            validate(instance=request.json, schema=WeatherReport.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        forecast = WeatherReport()
        forecast.deserialize(request.json, location.location_id, entry_type="forecast")
        try:
            db.session.add(forecast)
            db.session.commit()
        except KeyError as e:
            raise BadRequest(description=str(e)) from e
        except IntegrityError:
            raise Conflict(description="A forecast for this time already exists.")

        return Response(
            status=201,
            headers={
                "Location": url_for(
                    "api.weatherforecastitem", location=location, forecast=forecast
                )
            },
        )


class WeatherForecastItem(Resource):

    def get(self, location, forecast):
        return forecast.serialize()

    def put(self, location, forecast):
        if not request.json:
            raise UnsupportedMediaType(description="Request body must be JSON")
        try:
            validate(request.json, WeatherReport.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        if request.json.get("forecast_time") is None:
            raise BadRequest(description="Missing required field: forecast_time")

        forecast.deserialize(request.json, location.location_id, entry_type="forecast")

        try:
            db.session.add(forecast)
            db.session.commit()
        except IntegrityError:
            raise Conflict(
                description="A forecast for this '{forecast_time}, {location_id}' already exists.".format(
                    **request.json
                )
            )
        return Response(
            status=204,
            headers={
                "Location": url_for(
                    "api.weatherforecastitem", location=location, forecast=forecast
                )
            },
        )

    def delete(self, location, forecast):
        db.session.delete(forecast)
        db.session.commit()
        return Response(status=204)
