from flask import request, Response
from flask_restful import Resource
from weatherradar.models import WeatherReport
from weatherradar import db
from werkzeug.exceptions import BadRequest, UnsupportedMediaType, NotFound, Conflict
from jsonschema import validate, ValidationError
import json


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

        forecast = WeatherReport.deserialize(
            request.json, location.location_id, entry_type="forecast"
        )
        db.session.add(forecast)
        db.session.commit()
        return Response(
            response=json.dumps(forecast.serialize()),
            mimetype="application/json",
            status=201,
        )


class WeatherForecastItem(Resource):

    # todo
    def get(self, forecast):
        return forecast.serialize()

    # todo
    def put(self, forecast):
        pass

    # todo
    def delete(self, forecast):
        pass
