from flask import current_app, url_for
from flask_login import current_user
from flask_restful import Resource, abort
from atrium.auth import permissions
import jwt
import arrow


class PermissionsResource(Resource):
    def get(self):
        return permissions


class EnrollResource(Resource):
    def post(self, permission):
        if not current_user.is_admin():
            return abort(401)

        token = jwt.encode({
            'permission': permission,
            'iat': arrow.utcnow().datetime,
            'exp': arrow.utcnow().replace(weeks=1).datetime
        }, current_app.config['SECRET_KEY'])

        return {
            'permission': permission,
            'token': token,
            'enroll_url': url_for('enroll', token=token, _external=True)
        }