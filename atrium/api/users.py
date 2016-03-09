from flask_restful import Resource, marshal_with, reqparse, abort
from flask_login import login_required, current_user
from .fields import user_fields
from atrium.schemas import User
from atrium.auth import parse_permission


class UsersListResource(Resource):
    @login_required
    @marshal_with(user_fields)
    def get(self):
        return list(User.objects.all())


class UsersResource(Resource):
    @login_required
    @marshal_with(user_fields)
    def get(self, user_id):
        return User.objects.with_id(user_id)


class UsersPermissionsResource(Resource):
    @login_required
    @marshal_with(user_fields)
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('permission', type=str, required=True)
        args = parser.parse_args()

        if user_id == current_user.get_id():
            return abort(401)

        if current_user.is_admin():
            User.objects.with_id(user_id).update(add_to_set__permissions=args['permission'])
        else:
            permission = parse_permission(args['permission'])
            if permission['realm'] != 'club':
                return abort(401)
            club = permission['resource']
            if not current_user.has_any_permission('club', club, ['admin']):
                return abort(401)
            User.objects.with_id(user_id).update(add_to_set__permissions=args['permission'])

        return User.objects.with_id(user_id)

    @login_required
    @marshal_with(user_fields)
    def delete(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('permission', type=str, required=True)
        args = parser.parse_args()

        if user_id == current_user.get_id():
            return abort(401)

        if current_user.is_admin():
            User.objects.with_id(user_id).update(pull__permissions=args['permission'])
        else:
            permission = parse_permission(args['permission'])
            if permission['realm'] != 'club':
                return abort(401)
            club = permission['resource']
            if not current_user.has_any_permission('club', club, ['admin']):
                return abort(401)
            User.objects.with_id(user_id).update(pull__permissions=args['permission'])

        return User.objects.with_id(user_id)