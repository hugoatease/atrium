from flask_restful import Api
from .profile import ProfileResource, ProfileListResource, ProfilePhoto
from .club import ClubListResource, ClubResource, ClubMembersResource, ClubLogoResource, ClubPermissionsResource
from .event import EventListResource, EventResource, EventPoster
from .news import NewsListResource, NewsResource, NewsMediasResource
from .users import UsersListResource, UsersResource, UsersPermissionsResource
from .permissions import PermissionsResource, EnrollResource

api = Api()

api.add_resource(ProfileListResource, '/api/profiles')
api.add_resource(ProfileResource, '/api/profiles/<profile_id>')
api.add_resource(ProfilePhoto, '/api/profiles/<profile_id>/photo')

api.add_resource(ClubListResource, '/api/clubs')
api.add_resource(ClubResource, '/api/clubs/<club_slug>')
api.add_resource(ClubMembersResource, '/api/clubs/<club_slug>/members')
api.add_resource(ClubLogoResource, '/api/clubs/<club_slug>/logo')
api.add_resource(ClubPermissionsResource, '/api/clubs/<club_slug>/permissions')

api.add_resource(EventListResource, '/api/events')
api.add_resource(EventResource, '/api/events/<event_id>')
api.add_resource(EventPoster, '/api/events/<event_id>/poster')

api.add_resource(NewsListResource, '/api/news')
api.add_resource(NewsResource, '/api/news/<news_id>')
api.add_resource(NewsMediasResource, '/api/news/<news_id>/medias')

api.add_resource(UsersListResource, '/api/users')
api.add_resource(UsersResource, '/api/users/<user_id>')
api.add_resource(UsersPermissionsResource, '/api/users/<user_id>/permissions')

api.add_resource(PermissionsResource, '/api/permissions')
api.add_resource(EnrollResource, '/api/permissions/enroll/<permission>')
