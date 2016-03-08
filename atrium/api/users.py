from flask_restful import Resource, marshal_with, reqparse
from .fields import user_fields
from atrium.schemas import User


class UsersListResource(Resource):
    @marshal_with(user_fields)
    def get(self):
        return list(User.objects.all())


class UsersResource(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        return User.objects.with_id(user_id)


class UsersPermissionsResource(Resource):
    @marshal_with(user_fields)
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('permission', type=str, required=True)
        args = parser.parse_args()

        User.objects.with_id(user_id).update(add_to_set__permissions=args['permission'])

        return User.objects.with_id(user_id)

    @marshal_with(user_fields)
    def delete(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('permission', type=str, required=True)
        args = parser.parse_args()

        User.objects.with_id(user_id).update(pull__permissions=args['permission'])

        return User.objects.with_id(user_id)