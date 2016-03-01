from flask import Flask
from atrium.schemas import db
import settings
from atrium.api import api

app = Flask(__name__)
app.config.from_object(settings)

db.init_app(app)
api.init_app(app)