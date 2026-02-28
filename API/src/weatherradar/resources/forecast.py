from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from weatherradar.models import WeatherReport
from weatherradar import db
from werkzeug.exceptions import BadRequest, UnsupportedMediaType, NotFound, Conflict
from jsonschema import validate, ValidationError
import json


class WeatherForecasts(Resource):

    def get(self, location_route):
        """Get all forecasts for a location."""
        forecasts = WeatherReport.query.filter_by(
            location_id=location_route.location_id, entry_type="forecast"
        ).all()
        return Response(
            response=json.dumps([f.serialize() for f in forecasts]),
            mimetype="application/json",
            status=200,
        )

    def post(self, location_route):
        """Create a new forecast for a location."""
        if not request.json:
            raise UnsupportedMediaType(description="Request body must be JSON")

        try:
            validate(instance=request.json, schema=WeatherReport.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        forecast = WeatherReport.deserialize(
            request.json, location_route.location_id, entry_type="forecast"
        )
        try:
            db.session.add(forecast)
            db.session.commit()
        except KeyError as e:
            raise BadRequest(description=str(e)) from e
        except IntegrityError:
            raise Conflict(description="A forecast for this time already exists.")

        return Response(
            status=201,
            headers={"Location": url_for("api.weatherforecastitem", forecast=forecast)},
        )


class WeatherForecastItem(Resource):

    def get(self, forecast_route):
        return forecast_route.serialize()

    def put(self, forecast_route):
        if not request.json:
            raise UnsupportedMediaType(description="Request body must be JSON")
        try:
            validate(request.json, WeatherReport.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        if request.json.get("forecast_time") is None:
            raise BadRequest(description="Missing required field: forecast_time")
        if request.json["forecast_time"] != forecast_route.forecast_time:
            raise BadRequest(description="forecast_time in URL and body must match")

        forecast_route.deserialize(
            request.json, forecast_route.location_id, entry_type="forecast"
        )
        try:
            db.session.add(forecast_route)
            db.session.commit()
        except IntegrityError:
            raise Conflict(description="A forecast for this time already exists.")
        return Response(
            status=201,
            headers={
                "Location": url_for("api.weatherforecastitem", forecast=forecast_route)
            },
        )

    def delete(self, forecast_route):
        db.session.delete(forecast_route)
        db.session.commit()
        return Response(status=204)
