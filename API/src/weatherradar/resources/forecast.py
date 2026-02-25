from flask_restful import Resource
from weatherradar.models import WeatherReport

class WeatherForecasts(Resource):
    
    #todo
    def get(self):
        pass
    
    #todo
    def post(self):
        pass


class WeatherForecastItem(Resource):

    #todo
    def get(self, forecast):
        return forecast.serialize()

    #todo
    def put(self, forecast):
        pass

    #todo
    def delete(self, forecast):
        pass
