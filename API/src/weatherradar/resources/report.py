from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from API.src.weatherradar.models import WeatherReport
from API.src.weatherradar import db

class WeatherReports(Resource):

    def get(self, location):
        reports = WeatherReport.query.filter_by(location_id=location.location_id, entry_type="report").all()
        response_data = []
        for report in reports:
            response_data.append(report.serialize())
        return response_data
    
    def post(self, location):
        if not request.json:
            return {"error": "Invalid JSON"}, 415
        try:
            validate(request.json, WeatherReport.json_schema())
        except ValidationError as e:
            return {"error": f"Missing field: {str(e)}"}, 400
        
        weatherReport = WeatherReport()
        weatherReport.deserialize(request.json, location_id=location.location_id, entry_type="report")
        try:
            db.session.add(weatherReport)
            db.session.commit()
        except IntegrityError:
            return {"error": "Weather report for this location and timestamp already exists."}, 409

        return Response(
            status=201,
            headers={"Location": url_for("api.weatherreportitem", location=location, report=weatherReport)},
        )        
        
class WeatherReportItem(Resource):

    def get(self, location, report):
        return report.serialize()

    def put(self, location, report):
        if not request.json:
            return {"error": "Invalid JSON"}, 415
        try:
            validate(request.json, WeatherReport.json_schema())
        except ValidationError as e:
            return {"error": f"Missing field: {str(e)}"}, 400
        
        report.deserialize(request.json, location_id=location.location_id, entry_type="report")
        try:
            db.session.commit()
        except IntegrityError:
            return {"error": "Weather report for this location and timestamp already exists."}, 409
        return {"message": "Weather report updated successfully."}, 200
    
    def delete(self, location, report):
        db.session.delete(report)
        db.session.commit()

        return {"message": "Weather report deleted successfully."}, 200
