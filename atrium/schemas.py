from flask.ext.mongoengine import MongoEngine

db = MongoEngine()


class User(db.Document):
    sub = db.StringField(required=True)
    email = db.StringField(required=True)
    admin = db.BooleanField(required=True, default=False)
    permissions = db.ListField(db.StringField())


class Profile(db.Document):
    user = db.ReferenceField(User, required=True)
    first_name = db.StringField(required=True)
    last_name = db.StringField(required=True)
    photo = db.StringField()
    facebook_id = db.StringField()
    twitter_id = db.StringField()
    biography = db.StringField()
    birthday = db.DateTimeField()


class Club(db.Document):
    slug = db.StringField(primary_key=True, required=True)
    name = db.StringField(required=True)
    logo = db.StringField()
    description = db.StringField()
    members = db.ListField(db.ReferenceField(Profile))


class Place(db.EmbeddedDocument):
    name = db.StringField(required=True)
    address = db.StringField()


class Event(db.Document):
    name = db.StringField(required=True)
    club = db.ReferenceField(Club, required=True)
    description = db.StringField(required=True)
    start_date = db.DateTimeField(required=True)
    end_date = db.DateTimeField(required=True)
    poster = db.StringField()
    place = db.EmbeddedDocumentField(Place)

    meta = {
        'ordering': ['-start_date']
    }


class News(db.Document):
    name = db.StringField(required=True)
    club = db.ReferenceField(Club)
    date = db.DateTimeField(required=True)
    author = db.ReferenceField(Profile, required=True)
    headline = db.StringField()
    content = db.StringField(required=True)