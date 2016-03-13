from flask import Flask, render_template, redirect, request, session, url_for, got_request_exception
from flask_babel import Babel, format_datetime, format_date, format_time
import requests
from urllib import urlencode
from atrium.schemas import db
from atrium.schemas import Club, Event, News
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
import arrow
from flask_login import current_user, login_required
import os
import rollbar
import rollbar.contrib.flask
from urllib import quote

app = Flask(__name__)
app.config.from_object(settings)
app.config['MONGODB_SETTINGS'] = {
    'host': app.config['MONGODB_HOST'],
    'port': app.config['MONGODB_PORT'],
    'db': app.config['MONGODB_DB'],
    'tz_aware': True
}


login_manager.init_app(app)

s3conn = S3Connection(app.config['AWS_KEY'], app.config['AWS_SECRET'])

from atrium.api import api

db.init_app(app)
api.init_app(app)

if 'ROLLBAR_TOKEN' in app.config:
    rollbar.init(app.config['ROLLBAR_TOKEN'], 'flask',
                 root=os.path.dirname(os.path.realpath(__file__)), allow_logging_basic_config=False)

@app.before_first_request
def rollbar_handler():
    if 'ROLLBAR_TOKEN' in app.config:
        got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

babel = Babel(app)
@babel.localeselector
def get_locale():
    guess = request.accept_languages.best_match(['en', 'fr'])
    if not guess:
        guess = 'en'
    return guess

@app.context_processor
def date_processors():
    def datetime_processor(datetime):
        return format_datetime(datetime, format='medium')

    return dict(
        format_date=format_date,
        format_time=format_time,
        format_datetime=datetime_processor
    )


def get_clubs_with_stats():
    clubs = list(Club.objects.aggregate(
        {'$lookup': {'from': 'event', 'localField': '_id', 'foreignField': 'club', 'as': 'events'}},
        {'$lookup': {'from': 'news', 'localField': '_id', 'foreignField': 'club', 'as': 'news'}}
    ))

    def club_stats(club):
        upcoming = 0
        news_published = 0
        for event in club['events']:
            if arrow.get(event['start_date']) > arrow.utcnow():
                upcoming += 1

        for news in club['news']:
            if news['date'] > arrow.utcnow().replace(months=-1):
                news_published += 1

        if upcoming > 0:
            club['upcoming'] = upcoming

        if news_published > 0:
            club['news_published'] = news_published

        club['weight'] = upcoming + news_published

        return club

    clubs = map(club_stats, clubs)
    clubs = sorted(clubs, key=lambda club: club['weight'], reverse=True)
    return clubs

@app.route('/')
def index():
    clubs = get_clubs_with_stats()[0:6]

    news = News.objects(date__gte=str(arrow.utcnow().replace(months=-1))).all()

    current_events = Event.objects(end_date__gt=str(arrow.utcnow()), start_date__lte=str(arrow.utcnow())).order_by('end_date').all()
    next_events = Event.objects(start_date__gte=str(arrow.utcnow())).order_by('end_date').all()

    return render_template('index.html', clubs=clubs, news=news,
                           current_events=current_events, next_events=next_events)

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

    if 'next' in request.args:
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
@login_required
def editor():
    return render_template('editor.html')

@app.route('/editor/<path:path>')
@login_required
def editor_all(path):
    return render_template('editor.html')

@app.route('/clubs')
def clubs_list():
    clubs = get_clubs_with_stats()
    return render_template('clubs.html', clubs=clubs)

@app.route('/clubs/<club_slug>')
def clubs(club_slug):
    club = Club.objects.with_id(club_slug)
    next_event = Event.objects(club=club, end_date__gte=str(arrow.utcnow())).order_by('end_date').first()

    current_event = None
    if next_event is not None and arrow.get(next_event.end_date) > arrow.utcnow() > arrow.get(next_event.start_date):
        current_event = next_event

    next_events = list(Event.objects(club=club, end_date__gte=str(arrow.utcnow())).order_by('end_date').all())
    if next_event is not None:
        next_events.remove(next_event)

    past_events = Event.objects(club=club, end_date__lt=str(arrow.utcnow())).order_by('-end_date').all()

    news = News.objects(club=club).order_by('-end_date').all()

    return render_template('club.html',
                           club=club, current_event=current_event, next_event=next_event,
                           next_events=next_events, past_events=past_events, news=news)

@app.route('/events/<event_id>')
def events(event_id):
    event = Event.objects.with_id(event_id)

    gmaps = None
    if app.config['GOOGLE_API_KEY'] and event.place.address is not None:
        gmaps = "https://www.google.com/maps/embed/v1/place?" \
                "q=" + quote(event.place.address.encode('utf-8')) + "&key=" + app.config['GOOGLE_API_KEY']

    return render_template('events.html', event=event, gmaps=gmaps)

@app.route('/clubs/<club_slug>/events')
def club_events(club_slug):
    club = Club.objects.with_id(club_slug)
    next_event = Event.objects(club=club, end_date__gte=str(arrow.utcnow())).order_by('end_date').first()

    current_event = None
    if next_event is not None and arrow.get(next_event.end_date) > arrow.utcnow() > arrow.get(next_event.start_date):
        current_event = next_event

    next_events = list(Event.objects(club=club, end_date__gte=str(arrow.utcnow())).order_by('end_date').all())
    if next_event is not None:
        next_events.remove(next_event)

    past_events = Event.objects(club=club, end_date__lt=str(arrow.utcnow())).order_by('-end_date').all()

    return render_template('club_events.html', club=club, current_event=current_event, next_event=next_event,
                           next_events=next_events, past_events=past_events)


@app.route('/enroll/<token>')
@login_required
def enroll(token):
    token = jwt.decode(token, app.config['SECRET_KEY'])
    user = current_user.get_user()
    user.update(add_to_set__permissions=token['permission'])

    return redirect(url_for('editor'))