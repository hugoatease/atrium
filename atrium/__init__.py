from flask import Flask, render_template
from atrium.schemas import db
import settings
from atrium.api import api

app = Flask(__name__)
app.config.from_object(settings)

db.init_app(app)
api.init_app(app)

@app.route('/editor')
def editor():
    return render_template('editor.html')