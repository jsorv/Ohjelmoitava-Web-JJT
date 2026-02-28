from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter

from .models import Location
from .models import WeatherReport


class LocationConverter(BaseConverter):

    def to_python(self, value):
        try:
            location_id = int(value)
        except ValueError:
            raise NotFound(description="Invalid location ID format")
        
        location = Location.query.filter_by(location_id=location_id).first()
        if not location:
           raise NotFound(description="Location not found")
        return location
    
    def to_url(self, value):
        return str(value.location_id)
    
class ForecastConverter(BaseConverter):
    """Custom URL converter to fetch WeatherReport forecasts by ID."""

    def to_python(self, value):
        try:
            report_id = int(value)
        except ValueError:
            raise NotFound(description="Invalid forecast ID format")

        forecast = WeatherReport.query.filter_by(
            report_id=report_id, entry_type="forecast"
        ).first()
        if not forecast:
            raise NotFound(description="Forecast not found")
        return forecast

    def to_url(self, value):
        return str(value.report_id)
