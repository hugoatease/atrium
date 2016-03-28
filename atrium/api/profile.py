from flask import current_app, g
from flask_login import current_user, login_required
from flask_restful import Resource, abort
from flask_restful import reqparse, marshal_with
from .fields import profile_fields
import arrow
from atrium import s3conn
from boto.s3.key import Key
import werkzeug.datastructures
import bleach
from .bleachconfig import ALLOWED_TAGS, ALLOWED_STYLES, ALLOWED_ATTRIBUTES
from hashlib import md5


class ProfileListResource(Resource):
    @marshal_with(profile_fields)
    def get(self):
        return list(g.Profile.objects.all())


class ProfileResource(Resource):
    @marshal_with(profile_fields)
    def get(self, profile_id):
        if profile_id == 'me':
            return g.Profile.objects.filter(user=current_user.get_user()).first()
        else:
            return g.Profile.objects.with_id(profile_id)

    @login_required
    @marshal_with(profile_fields)
    def put(self, profile_id):
        if profile_id != 'me' and not current_user.is_admin():
            return abort(401)

        if profile_id == 'me':
            profile = g.Profile.objects.filter(user=current_user.get_user()).first()
        else:
            profile = g.Profile.objects.with_id(profile_id)

        parser = reqparse.RequestParser()
        parser.add_argument('facebook_id', type=unicode, store_missing=False)
        parser.add_argument('twitter_id', type=unicode, store_missing=False)
        parser.add_argument('biography', type=unicode, store_missing=False)
        parser.add_argument('birthday', type=unicode, store_missing=False)
        args = parser.parse_args()

        for field in ['facebook_id', 'twitter_id']:
            if field in args.keys():
                setattr(profile, field, args[field])

        if 'biography' in args.keys():
            profile.biography = bleach.clean(args['biography'], tags=ALLOWED_TAGS, styles=ALLOWED_STYLES, attributes=ALLOWED_ATTRIBUTES)

        if 'birthday' in args.keys():
            profile.birthday = arrow.get(args['birthday']).naive

        profile.save()
        return profile


class ProfilePhoto(Resource):
    @login_required
    @marshal_with(profile_fields)
    def post(self, profile_id):
        if profile_id != 'me' and not current_user.is_admin():
            return abort(401)

        if profile_id == 'me':
            profile = g.Profile.objects.filter(user=current_user.get_user()).first()
        else:
            profile = g.Profile.objects.with_id(profile_id)

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

    @login_required
    def delete(self, profile_id):
        if profile_id != 'me' and not current_user.is_admin():
            return abort(401)

        if profile_id == 'me':
            profile = g.Profile.objects.filter(user=current_user.get_user()).first()
        else:
            profile = g.Profile.objects.with_id(profile_id)

        photo_url = profile.photo

        profile.photo = 'https://secure.gravatar.com/avatar/' + md5(profile.user.email).hexdigest() + '?d=identicon&s=200'
        profile.save()

        if 'https://' + current_app.config['AWS_S3_BUCKET'] + '.s3.amazonaws.com/profiles/' in photo_url:
            bucket = s3conn.get_bucket(current_app.config['AWS_S3_BUCKET'])
            key = bucket.get_key('profiles/' + str(profile.id))
            key.delete()

        return '', 204