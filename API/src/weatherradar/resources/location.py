from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict, UnsupportedMediaType

from API.src.weatherradar.models import Location
from API.src.weatherradar import db

class Locations(Resource):
    
    def get(self):
        """Get all locations."""
        response_data = []
        locations = Location.query.all()
        for location in locations:
            response_data.append(location.serialize())
        return response_data

    def post(self):
        """Create a new location."""
        if not request.json:
            raise UnsupportedMediaType(description="Request body must be JSON")
        try:
            validate(request.json, Location.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        location = Location()
        location.deserialize(request.json)

        try:
            db.session.add(location)
            db.session.commit()
        except KeyError as e:
            raise BadRequest(description=str(e))
        except IntegrityError:
            raise Conflict(
                description="Location with name '{city}, {country}' already exists.".format(
                    **request.json
                )
            )

        return Response(
            status=201,
            headers={"Location": url_for("api.locationitem", location=location)}
        )


class LocationItem(Resource):

    def get(self, location):
        """Get a single location."""
        return location.serialize()

    def put(self, location):
        """Update an existing location."""
        if not request.json:
            raise UnsupportedMediaType(description="Request body must be JSON")
        try:
            validate(request.json, Location.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        location.deserialize(request.json)
        try:
            db.session.add(location)
            db.session.commit()
        except IntegrityError:
            raise Conflict(
                description="Location with name '{city}, {country}' already exists.".format(
                    **request.json
                )
            )

        return Response(status=204)

    def delete(self, location):
        """Delete an existing location."""
        db.session.delete(location)
        db.session.commit()
        return Response(status=204)
