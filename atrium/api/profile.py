from flask_restful import Resource
from atrium.schemas import Profile
from flask_restful import reqparse, marshal_with
from .fields import profile_fields
import arrow


class ProfileListResource(Resource):
    @marshal_with(profile_fields)
    def get(self):
        return list(Profile.objects.all())


class ProfileResource(Resource):
    @marshal_with(profile_fields)
    def get(self, profile_id):
        return Profile.objects.with_id(profile_id)

    @marshal_with(profile_fields)
    def put(self, profile_id):
        profile = Profile.objects.with_id(profile_id)

        parser = reqparse.RequestParser()
        parser.add_argument('facebook_id', type=unicode, store_missing=False)
        parser.add_argument('twitter_id', type=unicode, store_missing=False)
        parser.add_argument('biography', type=unicode, store_missing=False)
        parser.add_argument('birthday', type=unicode, store_missing=False)
        args = parser.parse_args()

        for field in ['facebook_id', 'twitter_id', 'biography']:
            if field in args.keys():
                setattr(profile, field, args[field])

        if 'birthday' in args.keys():
            profile.birthday = arrow.get(args['birthday']).naive

        profile.save()
        return profile