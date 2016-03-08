from flask import request
from flask_restful import Resource, marshal_with, reqparse, abort
from flask_login import current_user, login_required
from atrium.schemas import News, Club
from .fields import news_fields
import arrow


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
        parser.add_argument('content', type=unicode, required=True)
        args = parser.parse_args()

        if not current_user.is_admin() and not current_user.has_any_permission('club', args['club'], ['admin', 'news']):
            return abort(401)

        news = News(
            name=args['name'],
            club=args['club'],
            date=arrow.utcnow().datetime,
            author=current_user.get_profile(),
            headline=args['headline'],
            content=args['content']
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

        for field in ['name', 'club', 'author', 'headline', 'content']:
            if field in args.keys():
                setattr(news, field, args[field])

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