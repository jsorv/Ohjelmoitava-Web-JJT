from models import db
from models import app
context = app.app_context()
context.push()
db.create_all()
context.pop()
