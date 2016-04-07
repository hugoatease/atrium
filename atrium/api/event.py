from flask import request, current_app, g, url_for
from flask_login import login_required, current_user
from flask_restful import Resource, marshal_with, reqparse, abort
from atrium.schemas import Place
from .fields import event_fields
import arrow
import werkzeug.datastructures
from atrium import s3conn
from boto.s3.key import Key
import bleach
from .bleachconfig import ALLOWED_TAGS, ALLOWED_STYLES, ALLOWED_ATTRIBUTES
import requests
import pypandoc


class EventListResource(Resource):
    @marshal_with(event_fields)
    def get(self):
        query = g.Event.objects
        if 'club' in request.args:
            query = query.filter(club=g.Club.objects.with_id(request.args['club']))

        return list(query.all())

    @login_required
    @marshal_with(event_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('club', type=unicode, required=True)
        parser.add_argument('name', type=unicode, store_missing=False)
        parser.add_argument('description', type=unicode, store_missing=False)
        parser.add_argument('start_date', type=unicode, store_missing=False)
        parser.add_argument('end_date', type=unicode, store_missing=False)
        parser.add_argument('facebook_id', type=unicode, store_missing=False)
        parser.add_argument('place', type=dict, store_missing=False)
        args = parser.parse_args()

        if not current_user.is_admin() and not current_user.has_any_permission('club', args['club'], ['admin', 'events']):
            return abort(401)

        def event_from_args(args):
            event = g.Event(
                name=args['name'],
                club=args['club'],
                description=bleach.clean(args['description'], tags=ALLOWED_TAGS, styles=ALLOWED_STYLES, attributes=ALLOWED_ATTRIBUTES),
                start_date=arrow.get(args['start_date']).datetime,
                end_date=arrow.get(args['end_date']).datetime,
                facebook_id=args['facebook_id']
            )

            if 'place' in args.keys():
                event.place = Place(
                    name=args['place']['name'],
                    address=args['place']['address']
                )

            event.save()
            return event

        def event_from_facebook(args, data):
            event = g.Event(
                club=args['club'],
                facebook_id=data['id'],
                name=data['name'],
                start_date=arrow.get(data['start_time']).datetime,
            )

            if 'description' in data.keys():
                event.description = data['description'].replace('\n', '<br />')

            if 'end_time' in data.keys():
                event.end_date = arrow.get(data['end_time']).datetime
            else:
                event.end_date = arrow.get(data['start_time']).replace(hours=2).datetime

            if 'place' in data.keys():
                event.place = Place(
                    name=data['place']['name']
                )
                if 'location' in data['place'].keys():
                    event.address = data['place']['location']['street'] + ', ' + data['place']['location']['city'] \
                                  + ', ' + data['place']['location']['country']

            event.save()
            bucket = s3conn.get_bucket(current_app.config['AWS_S3_BUCKET'])
            key = Key(bucket)
            key.key = g.tenant + '/events/' + str(event.id)
            key.content_type = 'image/jpeg'
            key.set_contents_from_string(requests.get(data['cover']['source']).content)
            key.make_public()
            event.poster = 'https://' + current_app.config['AWS_S3_BUCKET'] + '.s3.amazonaws.com/' + g.tenant + '/events/' + str(event.id)
            event.save()

        if 'facebook_id' not in args.keys() or args['facebook_id'] is None:
            for key in ['name', 'description', 'start_date', 'end_date']:
                if key not in args.keys():
                    return abort(400)
            event = event_from_args(args)
        else:
            data = requests.get('https://graph.facebook.com/' + args['facebook_id'], params={
                'access_token': current_app.config['FACEBOOK_APPID'] + '|' + current_app.config['FACEBOOK_SECRET'],
                'fields': 'cover,name,description,place,start_time,end_time'
            }).json()
            event = event_from_facebook(args, data)

        return event


class EventResource(Resource):
    @marshal_with(event_fields)
    def get(self, event_id):
        return g.Event.objects.with_id(event_id)

    @login_required
    @marshal_with(event_fields)
    def put(self, event_id):
        event = g.Event.objects.with_id(event_id)

        if not current_user.is_admin() and not current_user.has_any_permission('club', event.club.id, ['admin', 'events']):
            return abort(401)

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, store_missing=False)
        parser.add_argument('description', type=unicode, store_missing=False)
        parser.add_argument('start_date', type=unicode, store_missing=False)
        parser.add_argument('end_date', type=unicode, store_missing=False)
        parser.add_argument('place', type=dict, store_missing=False)
        parser.add_argument('facebook_id', type=unicode, store_missing=False)
        args = parser.parse_args()

        for field in ['name', 'club', 'facebook_id']:
            if field in args.keys():
                setattr(event, field, args[field])

        for field in ['start_date', 'end_date']:
            if field in args.keys():
                setattr(event, field, arrow.get(args[field]).naive)

        if 'description' in args.keys():
            event.description = bleach.clean(args['description'], tags=ALLOWED_TAGS, styles=ALLOWED_STYLES, attributes=ALLOWED_ATTRIBUTES)

        if 'place' in args.keys():
            event.place = Place(name=args['place']['name'], address=args['place']['address'])

        event.save()
        return event

    @login_required
    def delete(self, event_id):
        event = g.Event.objects.with_id(event_id)
        if not current_user.is_admin() and not current_user.has_any_permission('club', event.club.id, ['admin', 'events']):
            return abort(401)

        event.delete()
        return '', 204


class EventPoster(Resource):
    @login_required
    @marshal_with(event_fields)
    def post(self, event_id):
        event = g.Event.objects.with_id(event_id)

        if not current_user.is_admin() and not current_user.has_any_permission('club', event.club.id, ['admin', 'events']):
            return abort(401)

        parser = reqparse.RequestParser()
        parser.add_argument('poster', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()

        bucket = s3conn.get_bucket(current_app.config['AWS_S3_BUCKET'])
        key = Key(bucket)
        key.key = g.tenant + '/events/' + str(event.id)
        key.content_type = args['poster'].mimetype
        key.set_contents_from_file(args['poster'].stream)
        key.make_public()

        event.poster = 'https://' + current_app.config['AWS_S3_BUCKET'] + '.s3.amazonaws.com/' + g.tenant + '/events/' + str(event.id)
        event.save()

        return event

    @login_required
    def delete(self, event_id):
        event = g.Event.objects.with_id(event_id)

        if not current_user.is_admin() and not current_user.has_any_permission('club', event.club.id, ['admin', 'events']):
            return abort(401)

        event.poster = None
        event.save()

        bucket = s3conn.get_bucket(current_app.config['AWS_S3_BUCKET'])
        key = bucket.get_key(g.tenant + '/events/' + str(event.id))
        key.delete()

        return '', 204


class EventFacebookPublish(Resource):
    @login_required
    def post(self, event_id):
        event = g.Event.objects.with_id(event_id)
        if not current_user.is_admin() and not current_user.has_any_permission('club', event.club.id, ['admin', 'events']):
            return abort(401)

        parser = reqparse.RequestParser()
        parser.add_argument('message', type=unicode, required=True)
        args = parser.parse_args()

        response = requests.post('https://graph.facebook.com/v2.5/' + event.club.facebook_publish.id + '/feed', params={
            'access_token': event.club.facebook_publish.access_token
        }, data={
            'message': args['message'],
            'link': url_for('events', event_id=event.id, _external=True)
        })

        return response.json()