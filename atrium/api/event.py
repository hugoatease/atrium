from flask import request, current_app
from flask_login import login_required, current_user
from flask_restful import Resource, marshal_with, reqparse, abort
from atrium.schemas import Event, Place, Club
from .fields import event_fields
import arrow
import werkzeug.datastructures
from atrium import s3conn
from boto.s3.key import Key
import bleach
from .bleachconfig import ALLOWED_TAGS, ALLOWED_STYLES, ALLOWED_ATTRIBUTES


class EventListResource(Resource):
    @marshal_with(event_fields)
    def get(self):
        query = Event.objects
        if 'club' in request.args:
            query = query.filter(club=Club.objects.with_id(request.args['club']))

        return list(query.all())

    @login_required
    @marshal_with(event_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, required=True)
        parser.add_argument('club', type=unicode, required=True)
        parser.add_argument('description', type=unicode, required=True)
        parser.add_argument('start_date', type=unicode, required=True)
        parser.add_argument('end_date', type=unicode, required=True)
        parser.add_argument('place', type=dict, store_missing=False)
        args = parser.parse_args()

        if not current_user.is_admin() and not current_user.has_any_permission('club', args['club'], ['admin', 'events']):
            return abort(401)

        event = Event(
            name=args['name'],
            club=args['club'],
            description=bleach.clean(args['description'], tags=ALLOWED_TAGS, styles=ALLOWED_STYLES, attributes=ALLOWED_ATTRIBUTES),
            start_date=arrow.get(args['start_date']).datetime,
            end_date=arrow.get(args['end_date']).datetime,
        )

        if 'place' in args.keys():
            event.place = Place(
                name=args['place']['name'],
                address=args['place']['address']
            )

        event.save()
        return event


class EventResource(Resource):
    @marshal_with(event_fields)
    def get(self, event_id):
        return Event.objects.with_id(event_id)

    @login_required
    @marshal_with(event_fields)
    def put(self, event_id):
        event = Event.objects.with_id(event_id)

        if not current_user.is_admin() and not current_user.has_any_permission('club', event.club.id, ['admin', 'events']):
            return abort(401)

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, store_missing=False)
        parser.add_argument('description', type=unicode, store_missing=False)
        parser.add_argument('start_date', type=unicode, store_missing=False)
        parser.add_argument('end_date', type=unicode, store_missing=False)
        parser.add_argument('place', type=dict, store_missing=False)
        args = parser.parse_args()

        for field in ['name', 'club']:
            if field in args.keys():
                setattr(event, field, args[field])

        for field in ['start_date', 'end_date']:
            if field in args.keys():
                setattr(event, field, arrow.get(args[field]).naive)

        if 'description' in args.keys():
            event.description = bleach.clean(args['description'], tags=ALLOWED_TAGS, styles=ALLOWED_STYLES, attributes=ALLOWED_ATTRIBUTES)
            print event.description

        if 'place' in args.keys():
            event.place = Place(name=args['place']['name'], address=args['place']['address'])

        event.save()
        return event

    @login_required
    def delete(self, event_id):
        event = Event.objects.with_id(event_id)
        if not current_user.is_admin() and not current_user.has_any_permission('club', event.club.id, ['admin', 'events']):
            return abort(401)

        event.delete()
        return '', 204


class EventPoster(Resource):
    @login_required
    @marshal_with(event_fields)
    def post(self, event_id):
        event = Event.objects.with_id(event_id)

        if not current_user.is_admin() and not current_user.has_any_permission('club', event.club.id, ['admin', 'events']):
            return abort(401)

        parser = reqparse.RequestParser()
        parser.add_argument('poster', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()

        bucket = s3conn.get_bucket(current_app.config['AWS_S3_BUCKET'])
        key = Key(bucket)
        key.key = 'events/' + str(event.id)
        key.content_type = args['poster'].mimetype
        key.set_contents_from_file(args['poster'].stream)
        key.make_public()

        event.poster = 'https://' + current_app.config['AWS_S3_BUCKET'] + '.s3.amazonaws.com/events/' + str(event.id)
        event.save()

        return event

    @login_required
    def delete(self, event_id):
        event = Event.objects.with_id(event_id)

        if not current_user.is_admin() and not current_user.has_any_permission('club', event.club.id, ['admin', 'events']):
            return abort(401)

        event.poster = None
        event.save()

        bucket = s3conn.get_bucket(current_app.config['AWS_S3_BUCKET'])
        key = bucket.get_key('events/' + str(event.id))
        key.delete()

        return '', 204