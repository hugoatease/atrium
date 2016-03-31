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


class ClubFacebookPublish(db.EmbeddedDocument):
    id = db.StringField(required=True)
    name = db.StringField(required=True)
    access_token = db.StringField(required=True)


class Club(db.Document):
    slug = db.StringField(primary_key=True, required=True)
    name = db.StringField(required=True)
    facebook_page = db.StringField()
    logo = db.StringField()
    description = db.StringField()
    members = db.ListField(db.ReferenceField(Profile))
    facebook_publish = db.EmbeddedDocumentField(ClubFacebookPublish)


class Place(db.EmbeddedDocument):
    name = db.StringField(required=True)
    address = db.StringField()


class Event(db.Document):
    name = db.StringField(required=True)
    club = db.ReferenceField(Club, required=True)
    description = db.StringField()
    start_date = db.DateTimeField(required=True)
    end_date = db.DateTimeField(required=True)
    poster = db.StringField()
    facebook_id = db.StringField()
    place = db.EmbeddedDocumentField(Place)

    meta = {
        'ordering': ['-start_date']
    }


class Media(db.EmbeddedDocument):
    name = db.StringField()
    url = db.StringField()


class News(db.Document):
    name = db.StringField(required=True)
    facebook_id = db.StringField()
    club = db.ReferenceField(Club, required=True)
    date = db.DateTimeField(required=True)
    author = db.ReferenceField(Profile, required=True)
    headline = db.StringField()
    content = db.StringField(required=True)
    draft = db.BooleanField(default=False)
    medias = db.EmbeddedDocumentListField(Media)

schemas = [User, Profile, Club, Event, News]