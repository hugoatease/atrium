from flask import request, current_app
from flask_restful import Resource, marshal_with, reqparse
from atrium.schemas import Event, Place, Club
from .fields import event_fields
import arrow
import werkzeug.datastructures
from atrium import s3conn
from boto.s3.key import Key


class EventListResource(Resource):
    @marshal_with(event_fields)
    def get(self):
        query = Event.objects
        if 'club' in request.args:
            query = query.filter(club=Club.objects.with_id(request.args['club']))

        return list(query.all())

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

        event = Event(
            name=args['name'],
            club=args['club'],
            description=args['description'],
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

    @marshal_with(event_fields)
    def put(self, event_id):
        event = Event.objects.with_id(event_id)

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, store_missing=False)
        parser.add_argument('club', type=unicode, store_missing=False)
        parser.add_argument('description', type=unicode, store_missing=False)
        parser.add_argument('start_date', type=unicode, store_missing=False)
        parser.add_argument('end_date', type=unicode, store_missing=False)
        parser.add_argument('place', type=dict, store_missing=False)
        args = parser.parse_args()

        for field in ['name', 'club', 'description']:
            if field in args.keys():
                setattr(event, field, args[field])

        for field in ['start_date', 'end_date']:
            if field in args.keys():
                setattr(event, field, arrow.get(args[field]).naive)

        if 'place' in args:
            event.place = Place(name=args['place']['name'], address=args['place']['address'])

        event.save()
        return event

    def delete(self, event_id):
        event = Event.objects.with_id(event_id)
        event.delete()
        return '', 204


class EventPoster(Resource):
    @marshal_with(event_fields)
    def post(self, event_id):
        event = Event.objects.with_id(event_id)

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