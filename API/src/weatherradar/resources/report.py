from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from jsonschema import validate

from weatherradar.models import WeatherReport
from weatherradar import db

class WeatherReports(Resource):

    #todo
    def get(self):
        response_data = []
        reports = WeatherReport.query.all()
        for report in reports:
            response_data.append(report.serialize())
        return response_data
    
    #todo
    def post(self):
        if not request.json:
            return {"error": "Invalid JSON"}, 415
        try:
            validate(request.json, WeatherReport.json_schema())
        except KeyError as e:
            return {"error": f"Missing field: {str(e)}"}, 400
        
        weatherReport = WeatherReport()
        weatherReport.deserialize(request.json)
        try:
            db.session.add(weatherReport)
            db.session.commit()
        except IntegrityError:
            return {"error": "Weather report for this location and timestamp already exists."}, 409
        return {"message": "Weather report created successfully."}, 201
        
class WeatherReportItem(Resource):

    def get(self, report):
        return report.serialize()

    def put(self, report):
        if not request.json:
            return {"error": "Invalid JSON"}, 415
        try:
            validate(request.json, WeatherReport.json_schema())
        except KeyError as e:
            return {"error": f"Missing field: {str(e)}"}, 400
        
        report.deserialize(request.json)
        try:
            db.session.commit()
        except IntegrityError:
            return {"error": "Weather report for this location and timestamp already exists."}, 409
        return {"message": "Weather report updated successfully."}, 200
    
    def delete(self, report):
        db.session.delete(report)
        db.session.commit()

        return {"message": "Weather report deleted successfully."}, 200
