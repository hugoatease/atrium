from flask import g
from flask_restful import Resource, marshal_with, reqparse, current_app, abort
from flask_login import login_required, current_user
from .fields import club_fields, club_permissions_fields
import werkzeug.datastructures
from atrium import s3conn
from boto.s3.key import Key
import bleach
from .bleachconfig import ALLOWED_TAGS, ALLOWED_STYLES, ALLOWED_ATTRIBUTES
import requests


class ClubListResource(Resource):
    @marshal_with(club_fields)
    def get(self):
        return list(g.Club.objects.all())

    @login_required
    @marshal_with(club_fields)
    def post(self):
        if not current_user.is_admin():
            return abort(401)

        parser = reqparse.RequestParser()
        parser.add_argument('slug', type=unicode, required=True)
        parser.add_argument('name', type=unicode, required=True)
        parser.add_argument('description', type=unicode, required=True)
        parser.add_argument('facebook_page', type=unicode)
        args = parser.parse_args()

        club = g.Club(
            slug=args['slug'],
            name=args['name'],
            description=bleach.clean(args['description'], tags=ALLOWED_TAGS, styles=ALLOWED_STYLES, attributes=ALLOWED_ATTRIBUTES),
            facebook_page=args['facebook_page']
        )

        club.save()
        return club


class ClubResource(Resource):
    @marshal_with(club_fields)
    def get(self, club_slug):
        return g.Club.objects.with_id(club_slug)

    @login_required
    @marshal_with(club_fields)
    def put(self, club_slug):
        if not current_user.is_admin() and not current_user.has_any_permission('club', club_slug, ['admin', 'edit']):
            return abort(401)

        club = g.Club.objects.with_id(club_slug)

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, store_missing=False)
        parser.add_argument('description', type=unicode, store_missing=False)
        parser.add_argument('facebook_page', type=unicode, store_missing=False)
        args = parser.parse_args()

        for field in ['name', 'facebook_page']:
            if field in args.keys():
                setattr(club, field, args[field])

        if 'description' in args.keys():
            club.description = bleach.clean(args['description'], tags=ALLOWED_TAGS, styles=ALLOWED_STYLES, attributes=ALLOWED_ATTRIBUTES)

        club.save()
        return club


class ClubMembersResource(Resource):
    @login_required
    def post(self, club_slug):
        if not current_user.is_admin() and not current_user.has_any_permission('club', club_slug, ['admin', 'edit']):
            return abort(401)

        club = g.Club.objects.with_id(club_slug)

        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=unicode)
        args = parser.parse_args()

        club.update(add_to_set__members=g.Profile.objects.with_id(args['profile_id']))

        return 'OK', 200

    @login_required
    def delete(self, club_slug):
        if not current_user.is_admin() and not current_user.has_any_permission('club', club_slug, ['admin', 'edit']):
            return abort(401)

        club = g.Club.objects.with_id(club_slug)

        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=unicode)
        args = parser.parse_args()

        club.update(pull__members=g.Profile.objects.with_id(args['profile_id']))

        return 'DELETED', 204


class ClubLogoResource(Resource):
    @login_required
    @marshal_with(club_fields)
    def post(self, club_slug):
        if not current_user.is_admin() and not current_user.has_any_permission('club', club_slug, ['admin', 'edit']):
            return abort(401)

        club = g.Club.objects.with_id(club_slug)

        parser = reqparse.RequestParser()
        parser.add_argument('logo', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()

        bucket = s3conn.get_bucket(current_app.config['AWS_S3_BUCKET'])
        key = Key(bucket)
        key.key = g.tenant + '/clubs/' + str(club.id)
        key.content_type = args['logo'].mimetype
        key.set_contents_from_file(args['logo'].stream)
        key.make_public()

        club.logo = 'https://' + current_app.config['AWS_S3_BUCKET'] + '.s3.amazonaws.com/' + g.tenant + '/clubs/' + str(club.id)
        club.save()

        return club

    @login_required
    def delete(self, club_slug):
        if not current_user.is_admin() and not current_user.has_any_permission('club', club_slug, ['admin', 'edit']):
            return abort(401)

        club = g.Club.objects.with_id(club_slug)
        club.logo = None
        club.save()

        bucket = s3conn.get_bucket(current_app.config['AWS_S3_BUCKET'])
        key = bucket.get_key(g.tenant + '/clubs/' + str(club.id))
        key.delete()

        return '', 204


class ClubPermissionsResource(Resource):
    @login_required
    @marshal_with(club_permissions_fields)
    def get(self, club_slug):
        permissions = list(g.User.objects.aggregate(
            {'$match': {'permissions': {'$exists': True}}},
            {'$unwind': '$permissions'},
            {'$match': {'permissions': {'$regex': 'club:' + club_slug + '::'}}},
            {'$group': {'_id': '$permissions', 'users': {'$push': '$_id'}}}
        ))

        def permissions_parse(permission):
            def fetch_profiles(user):
                return g.Profile.objects(user=user).first()
            profiles = map(fetch_profiles, permission['users'])
            permission['profiles'] = profiles
            return permission

        parsed_permissions = map(permissions_parse, permissions)
        return parsed_permissions


class ClubFacebookEventsResource(Resource):
    def get(self, club_slug):
        club = g.Club.objects.with_id(club_slug)
        if club.facebook_page is None:
            return abort(404)

        events = []
        end = False
        next = None
        while not end:
            params = {
                'access_token': current_app.config['FACEBOOK_APPID'] + '|' + current_app.config['FACEBOOK_SECRET'],
                'fields': 'id,name,start_time,end_time',
            }
            if next is not None:
                params['after'] = next
            response = requests.get('https://graph.facebook.com/' + club.facebook_page + '/events', params=params).json()
            if len(response['data']) == 0:
                end = True
            else:
                events += response['data']
                next = response['paging']['cursors']['after']

        def filter_events(item):
            event = g.Event.objects(facebook_id=item['id']).first()
            if event is None:
                return True
            return False

        events = filter(filter_events, events)

        return events