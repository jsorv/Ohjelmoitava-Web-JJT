from src.weatherradar.models import db
from src.weatherradar.models import app

context = app.app_context()
context.push()
db.create_all()
context.pop()
