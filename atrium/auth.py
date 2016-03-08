from flask_login import LoginManager, UserMixin
from .schemas import User, Profile

login_manager = LoginManager()


def build_permission(realm, resource, permission):
    return realm + ':' + resource + '::' + permission


def parse_permission(permission):
    realm = permission.split(':', 1)[0]
    resource = permission.split(':', 1)[1].split('::', 1)[0]
    perm = permission.split('::', 1)[1]
    return {
        'realm': realm,
        'resource': resource,
        'permission': perm
    }


class UserHandler(UserMixin):
    def __init__(self, user):
        self.user = user

    def get_id(self):
        return str(self.user.id)

    def is_admin(self):
        return self.user.admin

    def get_user(self):
        return self.user

    def get_profile(self):
        return Profile.objects(user=self.user).first()

    def has_permission(self, permission):
        if 'permissions' not in self.user:
            return False
        if permission in self.user.permissions:
            return True

        return False

    def has_any_permission(self, realm, resource, permissions):
        for permission in permissions:
            if self.has_permission(build_permission(realm, resource, permission)):
                return True
        return False

@login_manager.user_loader
def load_user(user_id):
    return UserHandler(User.objects.with_id(user_id))