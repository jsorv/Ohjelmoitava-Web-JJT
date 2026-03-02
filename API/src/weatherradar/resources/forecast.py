from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType, NotFound, Conflict
from jsonschema import validate, ValidationError
import json

from API.src.weatherradar.models import WeatherReport
from API.src.weatherradar import db


class WeatherForecasts(Resource):
    """Resource for managing weather forecasts for a specific location."""

    def get(self, location):
        """Get all forecasts for a location.

        Parameters:
            location (Location): The location for which to retrieve forecasts.
            Returns a list of forecasts for the specified location.
        """
        forecasts = WeatherReport.query.filter_by(
            location_id=location.location_id, entry_type="forecast"
        ).all()
        return Response(
            response=json.dumps([f.serialize() for f in forecasts]),
            mimetype="application/json",
            status=200,
        )

    def post(self, location):
        """Create a new forecast for a location.
        Parameters:
            location (Location): The location for which to create a forecast.
            The request body must be a JSON object containing the forecast data.
            Returns a 201 Created response with a Location header pointing to the new forecast.
        """
        if request.content_type != "application/json":
            raise UnsupportedMediaType(
                description="Content-Type must be application/json"
            )

        try:
            validate(instance=request.json, schema=WeatherReport.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        if request.json.get("forecast_time") is None:
            raise BadRequest(description="Missing required field: forecast_time")

        forecast = WeatherReport()
        forecast.deserialize(request.json, location.location_id, entry_type="forecast")
        try:
            db.session.add(forecast)
            db.session.commit()
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
    """Resource for managing a specific weather forecast."""

    def get(self, location, forecast):
        """Get a specific forecast for a location.
        Parameters:
            location (Location): The location for which to retrieve the forecast.
            forecast (WeatherReport): The specific forecast to retrieve.
        """
        return forecast.serialize()

    def put(self, location, forecast):
        """Update a specific forecast for a location.
        Parameters:
            location (Location): The location for which to update the forecast.
            forecast (WeatherReport): The specific forecast to update.
            The request body must be a JSON object containing the updated forecast data.
            Forecast time is required for updates.
            Returns a 204 No Content response if the update is successful.
        """
        if request.content_type != "application/json":
            raise UnsupportedMediaType(
                description="Content-Type must be application/json"
            )
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
        """Delete a specific forecast for a location.
        Parameters:
            location (Location): The location for which to delete the forecast.
            forecast (WeatherReport): The specific forecast to delete.
            Returns a 204 No Content response if the deletion is successful.
        """
        db.session.delete(forecast)
        db.session.commit()
        return Response(status=204)
