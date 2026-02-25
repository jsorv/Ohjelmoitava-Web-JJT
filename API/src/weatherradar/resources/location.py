from flask_restful import Resource
from weatherradar.models import Location

class Locations(Resource):

    #todo
    def get(self):
        pass
    
    #todo
    def post(self):
        pass


class LocationItem(Resource):

    #todo
    def get(self, location):
        return location.serialize()

    #todo
    def put(self, location):
        pass
    
    #todo
    def delete(self, location):
        pass
