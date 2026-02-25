from flask_restful import Resource
from weatherradar.models import WeatherReport

class WeatherReports(Resource):

    #todo
    def get(self):
        pass
    
    #todo
    def post(self):
        pass


class WeatherReportItem(Resource):

    #todo
    def get(self, report):
        return report.serialize()

    #todo
    def put(self, report):
        pass
    
    #todo
    def delete(self, report):
        pass
