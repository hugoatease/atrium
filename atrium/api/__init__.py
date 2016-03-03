from flask_restful import Api
from .profile import ProfileResource, ProfileListResource, ProfilePhoto
from .club import ClubListResource, ClubResource, ClubMembersResource
from .event import EventListResource, EventResource
from .news import NewsListResource, NewsResource

api = Api()

api.add_resource(ProfileListResource, '/api/profiles')
api.add_resource(ProfileResource, '/api/profiles/<profile_id>')
api.add_resource(ProfilePhoto, '/api/profiles/<profile_id>/photo')

api.add_resource(ClubListResource, '/api/clubs')
api.add_resource(ClubResource, '/api/clubs/<club_slug>')
api.add_resource(ClubMembersResource, '/api/clubs/<club_slug>/members')

api.add_resource(EventListResource, '/api/events')
api.add_resource(EventResource, '/api/events/<event_id>')

api.add_resource(NewsListResource, '/api/news')
api.add_resource(NewsResource, '/api/news/<news_id>')

