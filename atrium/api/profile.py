from flask_login import current_user
from flask_restful import Resource
from atrium.schemas import Profile
from flask_restful import reqparse, marshal_with
from .fields import profile_fields
import arrow
from atrium import s3conn
from flask import current_app
from boto.s3.key import Key
import werkzeug.datastructures


class ProfileListResource(Resource):
    @marshal_with(profile_fields)
    def get(self):
        return list(Profile.objects.all())


class ProfileResource(Resource):
    @marshal_with(profile_fields)
    def get(self, profile_id):
        if profile_id == 'me':
            return Profile.objects.filter(user=current_user.get_user()).first()
        else:
            return Profile.objects.with_id(profile_id)

    @marshal_with(profile_fields)
    def put(self, profile_id):
        if profile_id == 'me':
            profile = Profile.objects.filter(user=current_user.get_user()).first()
        else:
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


class ProfilePhoto(Resource):
    @marshal_with(profile_fields)
    def post(self, profile_id):
        if profile_id == 'me':
            profile = Profile.objects.filter(user=current_user.get_user()).first()
        else:
            profile = Profile.objects.with_id(profile_id)

        parser = reqparse.RequestParser()
        parser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()

        bucket = s3conn.get_bucket(current_app.config['AWS_S3_BUCKET'])
        key = Key(bucket)
        key.key = 'profiles/' + str(profile.id)
        key.content_type = args['photo'].mimetype
        key.set_contents_from_file(args['photo'].stream)
        key.make_public()

        profile.photo = 'https://' + current_app.config['AWS_S3_BUCKET'] + '.s3.amazonaws.com/profiles/' + str(profile.id)
        profile.save()

        return profile