from flask import Blueprint
from flask_restful import Api

from weatherradar.resources.location import Locations, LocationItem
from weatherradar.resources.forecast import WeatherForecasts, WeatherForecastItem
from weatherradar.resources.report import WeatherReports, WeatherReportItem

# from . import views

api_bp = Blueprint("api", __name__, url_prefix="/api")


api = Api(api_bp)

# api_bp.add_url_rule("/", "entry", views.entry)

api.add_resource(Locations, "/locations/")
api.add_resource(LocationItem, "/locations/<location:location>/")

api.add_resource(WeatherForecasts, "/locations/<location:location>/forecasts/")
api.add_resource(
    WeatherForecastItem, "/locations/<location:location>/forecasts/<forecast:forecast>/"
)

api.add_resource(WeatherReports, "/locations/<location:location>/reports/")
api.add_resource(
    WeatherReportItem, "/locations/<location:location>/reports/<report:report>/"
)
