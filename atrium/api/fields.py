from flask_restful import fields

user_fields = {
    'id': fields.String,
    'sub': fields.String,
    'email': fields.String,
    'admin': fields.Boolean,
    'permissions': fields.List(fields.String)
}

profile_list_fields = {
    'id': fields.String,
    'user': fields.String(attribute=lambda profile: profile.user.id),
    'first_name': fields.String,
    'last_name': fields.String,
    'photo': fields.String,
    'facebook_id': fields.String,
    'twitter_id': fields.String,
    'biography': fields.String,
    'birthday': fields.DateTime
}

profile_fields = {
    'id': fields.String,
    'user': fields.Nested(user_fields),
    'first_name': fields.String,
    'last_name': fields.String,
    'photo': fields.String,
    'facebook_id': fields.String,
    'twitter_id': fields.String,
    'biography': fields.String,
    'birthday': fields.DateTime
}

facebook_publish = {
    'id': fields.String,
    'name': fields.String
}

club_list_fields = {
    'id': fields.String,
    'slug': fields.String,
    'name': fields.String,
    'facebook_page': fields.String,
    'logo': fields.String,
    'description': fields.String,
}

club_fields = {
    'id': fields.String,
    'slug': fields.String,
    'name': fields.String,
    'facebook_page': fields.String,
    'logo': fields.String,
    'description': fields.String,
    'members': fields.List(fields.Nested(profile_list_fields)),
    'facebook_publish': fields.Nested(facebook_publish)
}

place_fields = {
    'name': fields.String,
    'address': fields.String
}

event_fields = {
    'id': fields.String,
    'name': fields.String,
    'club': fields.String(attribute=lambda event: event.club.id),
    'facebook_id': fields.String,
    'description': fields.String,
    'start_date': fields.String,
    'end_date': fields.String,
    'poster': fields.String,
    'place': fields.Nested(place_fields)
}

media_fields = {
    'name': fields.String,
    'url': fields.String
}

news_fields = {
    'id': fields.String,
    'name': fields.String,
    'club': fields.String(attribute=lambda news: news.club.id),
    'date': fields.String,
    'draft': fields.Boolean,
    'author': fields.Nested(profile_list_fields),
    'headline': fields.String,
    'content': fields.String,
    'medias': fields.List(fields.Nested(media_fields))
}

club_permissions_fields = {
    '_id': fields.String,
    'profiles': fields.List(fields.Nested(profile_list_fields))
}