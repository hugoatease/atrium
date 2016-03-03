from flask_restful import Resource, marshal_with, reqparse
from .fields import club_fields
from atrium.schemas import Club, Profile


class ClubListResource(Resource):
    @marshal_with(club_fields)
    def get(self):
        return list(Club.objects.all())

    @marshal_with(club_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('slug', type=unicode, required=True)
        parser.add_argument('name', type=unicode, required=True)
        parser.add_argument('description', type=unicode, required=True)
        args = parser.parse_args()

        club = Club(
            slug=args['slug'],
            name=args['name'],
            description=args['description']
        )

        club.save()
        return club


class ClubResource(Resource):
    @marshal_with(club_fields)
    def get(self, club_slug):
        return Club.objects.with_id(club_slug)

    @marshal_with(club_fields)
    def put(self, club_slug):
        club = Club.objects.with_id(club_slug)

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, store_missing=False)
        parser.add_argument('description', type='unicode', store_missing=False)
        args = parser.parse_args()

        for field in ['name', 'description']:
            if field in args.keys():
                setattr(club, field, args[field])

        club.save()
        return club


class ClubMembersResource(Resource):
    def post(self, club_slug):
        club = Club.objects.with_id(club_slug)

        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=unicode)
        args = parser.parse_args()

        club.update(add_to_set__members=Profile.objects.with_id(args['profile_id']))

        return 'OK', 200

    def delete(self, club_slug):
        club = Club.objects.with_id(club_slug)

        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=unicode)
        args = parser.parse_args()

        club.update(pull__members=Profile.objects.with_id(args['profile_id']))

        return 'DELETED', 204