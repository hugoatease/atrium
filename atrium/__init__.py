from flask import Flask, render_template, redirect, request, session, url_for
import requests
from urllib import urlencode
from atrium.schemas import db
import settings
from .auth import login_manager
import jwt
import cryptography.hazmat.primitives.serialization
from cryptography.hazmat.backends import default_backend
from flask_login import login_user, logout_user
from .auth import UserHandler
from .schemas import User, Profile
from boto.s3.connection import S3Connection
from hashlib import md5

app = Flask(__name__)
app.config.from_object(settings)

login_manager.init_app(app)

s3conn = S3Connection(app.config['AWS_KEY'], app.config['AWS_SECRET'])

from atrium.api import api

db.init_app(app)
api.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    params = {
        'scope': 'openid profile email',
        'response_type': 'code',
        'client_id': app.config['OPENID_CLIENT'],
        'redirect_uri': app.config['OPENID_REDIRECT']
    }

    if 'signup_redirect' in request.args:
        params['signup_redirect'] = 'true'

    params = urlencode(params)

    if 'login_next' in request.args:
        session['login_next'] = request.args['next']

    return redirect(app.config['OPENID_AUTHORIZE_ENDPOINT'] + '?' + params)

@app.route('/login/return')
def login_return():
    code = request.args['code']
    clientAuth = requests.auth.HTTPBasicAuth(app.config['OPENID_CLIENT'], app.config['OPENID_SECRET'])
    tokens = requests.post(app.config['OPENID_TOKEN_ENDPOINT'], auth=clientAuth, data={
        'grant_type': 'authorization_code',
        'redirect_uri': app.config['OPENID_REDIRECT'],
        'code': code
    }).json()

    key = cryptography.hazmat.primitives.serialization.load_pem_public_key(app.config['OPENID_ISSUER_KEY'], backend=default_backend())

    sub = jwt.decode(tokens['id_token'], key, audience=app.config['OPENID_CLIENT'])['sub']
    info = requests.get(app.config['OPENID_USERINFO_ENDPOINT'], headers={'Authorization': 'Bearer ' + tokens['access_token']}).json()

    print User.objects.filter(sub=sub).first()

    if User.objects.filter(sub=sub).first() is None:
        user = User(sub=sub, email=info['email'])
        user.save()
        profile = Profile(
            user=user,
            first_name=info['given_name'],
            last_name=info['family_name'],
            photo='https://secure.gravatar.com/avatar/' + md5(info['email']).hexdigest() + '?d=identicon&s=200'
        )
        profile.save()
    else:
        user = User.objects.filter(sub=sub).first()
        user.email = info['email']
        user.save()
        profile = Profile.objects.filter(user=user).first()
        profile.first_name = info['given_name']
        profile.last_name = info['family_name']
        profile.save()

    login_user(UserHandler(user))

    if 'login_next' not in session:
        return redirect('/')
    else:
        return redirect(session['login_next'])

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/editor')
def editor():
    return render_template('editor.html')

@app.route('/editor/<path:path>')
def editor_all(path):
    return render_template('editor.html')