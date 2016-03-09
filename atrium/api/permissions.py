from flask_restful import Resource
from atrium.auth import permissions


class PermissionsResource(Resource):
    def get(self):
        return permissions