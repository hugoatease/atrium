from flask_login import LoginManager, UserMixin
from .schemas import User

login_manager = LoginManager()


class UserHandler(UserMixin):
    def __init__(self, user):
        self.user = user

    def get_id(self):
        return str(self.user.id)

    def is_admin(self):
        return self.user.admin

    def get_user(self):
        return self.user


@login_manager.user_loader
def load_user(user_id):
    return UserHandler(User.objects.with_id(user_id))