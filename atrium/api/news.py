from flask import request, current_app
from flask_restful import Resource, marshal_with, reqparse, abort
from flask_login import current_user, login_required
from atrium.schemas import News, Club, Media
from .fields import news_fields
import arrow
import bleach
from .bleachconfig import ALLOWED_TAGS, ALLOWED_STYLES, ALLOWED_ATTRIBUTES
from atrium import s3conn
from boto.s3.key import Key
import werkzeug.datastructures
from uuid import uuid4


class NewsListResource(Resource):
    @marshal_with(news_fields)
    def get(self):
        query = News.objects
        if 'club' in request.args:
            query = query.filter(club=Club.objects.with_id(request.args['club']))

        return list(query.all())

    @login_required
    @marshal_with(news_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, required=True)
        parser.add_argument('club', type=unicode)
        parser.add_argument('headline', type=unicode, required=True)
        parser.add_argument('content', type=unicode)
        args = parser.parse_args()

        if not current_user.is_admin() and not current_user.has_any_permission('club', args['club'], ['admin', 'news']):
            return abort(401)

        news = News(
            name=args['name'],
            club=args['club'],
            date=arrow.utcnow().datetime,
            author=current_user.get_profile(),
            headline=args['headline'],
            content=bleach.clean(args['content'], tags=ALLOWED_TAGS, styles=ALLOWED_STYLES, attributes=ALLOWED_ATTRIBUTES)
        )

        news.save()
        return news


class NewsResource(Resource):
    @marshal_with(news_fields)
    def get(self, news_id):
        return News.objects.with_id(news_id)

    @login_required
    @marshal_with(news_fields)
    def put(self, news_id):
        news = News.objects.with_id(news_id)

        if not current_user.is_admin() and not current_user.has_any_permission('club', news.club.id, ['admin', 'news']):
            return abort(401)

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=unicode, store_missing=False)
        parser.add_argument('date', type=unicode, store_missing=False)
        parser.add_argument('author', type=unicode, store_missing=False)
        parser.add_argument('headline', type=unicode, store_missing=False)
        parser.add_argument('content', type=unicode, store_missing=False)
        args = parser.parse_args()

        for field in ['name', 'club', 'author', 'headline']:
            if field in args.keys():
                setattr(news, field, args[field])

        if 'content' in args.keys():
            news.content = bleach.clean(args['content'], tags=ALLOWED_TAGS, styles=ALLOWED_STYLES, attributes=ALLOWED_ATTRIBUTES)

        if 'date' in args.keys():
            news.date = arrow.get(args['date']).naive

        news.save()
        return news

    @login_required
    def delete(self, news_id):
        news = News.objects.with_id(news_id)
        if not current_user.is_admin() and not current_user.has_any_permission('club', news.club.id, ['admin', 'news']):
            return abort(401)

        news.delete()
        return '', 204


class NewsMediasResource(Resource):
    @marshal_with(news_fields)
    def post(self, news_id):
        news = News.objects.with_id(news_id)

        if not current_user.is_admin() and not current_user.has_any_permission('club', news.club.id, ['admin', 'news']):
            return abort(401)

        parser = reqparse.RequestParser()
        parser.add_argument('media', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()

        uid = str(uuid4())

        bucket = s3conn.get_bucket(current_app.config['AWS_S3_BUCKET'])
        key = Key(bucket)
        key.key = 'news/' + str(news.id) + '/' + uid
        key.content_type = args['media'].mimetype
        key.set_contents_from_file(args['media'].stream)
        key.make_public()

        news.update(add_to_set__medias=Media(
            name=uid,
            url='https://' + current_app.config['AWS_S3_BUCKET'] + '.s3.amazonaws.com/news/' + str(news.id) + '/' + uid
        ))

        return News.objects.with_id(news_id)