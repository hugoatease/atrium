from flask_restful import fields

user_fields = {
    'sub': fields.String,
    'email': fields.String,
    'admin': fields.Boolean
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

club_fields = {
    'slug': fields.String,
    'name': fields.String,
    'logo': fields.String,
    'description': fields.String,
    'members': fields.List(fields.Nested(profile_fields))
}

place_fields = {
    'name': fields.String,
    'address': fields.String
}

event_fields = {
    'id': fields.String,
    'name': fields.String,
    'club': fields.Nested(club_fields),
    'description': fields.String,
    'start_date': fields.String,
    'end_date': fields.String,
    'poster': fields.String,
    'place': fields.Nested(place_fields)
}

news_fields = {
    'id': fields.String,
    'name': fields.String,
    'club': fields.Nested(club_fields),
    'date': fields.String,
    'author': fields.Nested(profile_fields),
    'headline': fields.String,
    'content': fields.String
}