from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.news import News


def abort_if_user_not_found(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f"News {news_id} not found")


class NewsResource(Resource):
    def get(self, news_id):
        abort_if_user_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        return jsonify({'News': news.to_dict(
            only=("id", "make", "name_bot"))})


class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        news = session.query(News).all()
        return jsonify({'News': [item.to_dict(
            only=("id", "make", "name_bot",)) for item in news]})
