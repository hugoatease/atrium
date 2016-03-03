from flask_restful import Resource, marshal_with, reqparse, current_app
from .fields import club_fields
from atrium.schemas import Club, Profile
import werkzeug.datastructures
from atrium import s3conn
from boto.s3.key import Key


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


class ClubLogoResource(Resource):
    @marshal_with(club_fields)
    def post(self, club_slug):
        club = Club.objects.with_id(club_slug)

        parser = reqparse.RequestParser()
        parser.add_argument('logo', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()

        bucket = s3conn.get_bucket(current_app.config['AWS_S3_BUCKET'])
        key = Key(bucket)
        key.key = 'clubs/' + str(club.id)
        key.content_type = args['logo'].mimetype
        key.set_contents_from_file(args['logo'].stream)
        key.make_public()

        club.logo = 'https://' + current_app.config['AWS_S3_BUCKET'] + '.s3.amazonaws.com/clubs/' + str(club.id)
        club.save()

        return club