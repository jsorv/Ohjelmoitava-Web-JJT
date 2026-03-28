"""Resource for managing locations."""

from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict, UnsupportedMediaType

from API.weatherradar import db


class Locations(Resource):
    """Resource for managing locations."""

    def get(self):
        """Get all locations.

        Returns a list of forecasts for the specified location.
        """
        from API.weatherradar.models import Location

        response_data = []
        locations = Location.query.all()
        for location in locations:
            response_data.append(location.serialize())
        return response_data

    def post(self):
        """Create a new location.

        The request body must be a JSON object containing the location data.
        Returns a 201 Created response with a Location header pointing to the new location.
        """
        from API.weatherradar.models import Location

        if request.content_type != "application/json":
            raise UnsupportedMediaType(
                description="Content-Type must be application/json"
            )
        try:
            validate(request.json, Location.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        location = Location()
        location.deserialize(request.json)

        try:
            db.session.add(location)
            db.session.commit()
        except KeyError as e:
            raise BadRequest(description=str(e)) from e
        except IntegrityError as exc:
            raise Conflict(
                description=f"Location with name '{request.json.get('city')}, {request.json.get('country')}' already exists."
            ) from exc

        return Response(
            status=201,
            headers={"Location": url_for("api.locationitem", location=location)},
        )


class LocationItem(Resource):
    """Resource for managing a specific location."""

    def get(self, location):
        """Get a single location.
        Parameters:
            location (Location): The location to retrieve.
        """
        return location.serialize()

    def put(self, location):
        """Update an existing location.
        Parameters:
            location (Location): The location to update.
        The request body must be a JSON object containing the updated location data.
        Returns a 204 No Content response if the update is successful.
        """
        from API.weatherradar.models import Location

        if request.content_type != "application/json":
            raise UnsupportedMediaType(
                description="Content-Type must be application/json"
            )
        try:
            validate(request.json, Location.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        location.deserialize(request.json)
        try:
            db.session.add(location)
            db.session.commit()
        except IntegrityError as exc:
            raise Conflict(
                description=f"Location with name '{request.json.get('city')}, {request.json.get('country')}' already exists."
            ) from exc

        return Response(status=204)

    def delete(self, location):
        """Delete an existing location.
        Parameters:
            location (Location): The location to delete.
        Returns a 204 No Content response if the deletion is successful.
        """
        db.session.delete(location)
        db.session.commit()
        return Response(status=204)
