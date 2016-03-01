from flask_restful import Resource, marshal_with, reqparse
from atrium.schemas import Event, Place
from .fields import event_fields
import arrow


class EventListResource(Resource):
    @marshal_with(event_fields)
    def get(self):
        return list(Event.objects.all())

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
            start_date=arrow.get(args['start_date']).naive,
            end_date=arrow.get(args['end_date']).naive,
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
                setattr(event, field, arrow.get(field).naive)

        if 'place' in args:
            event.place = Place(name=args['place']['name'], address=args['place']['address'])

        event.save()
        return event

    def delete(self, event_id):
        event = Event.objects.with_id(event_id)
        event.delete()
        return '', 204