from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.reviews import Reviwes


def abort_if_user_not_found(rew_id):
    session = db_session.create_session()
    rew = session.query(Reviwes).get(rew_id)
    if not rew:
        abort(404, message=f"Review {rew_id} not found")


class ReviewResource(Resource):
    def get(self, rew_id):
        abort_if_user_not_found(rew_id)
        session = db_session.create_session()
        rew = session.query(Reviwes).get(rew_id)
        return jsonify({'Reviews': rew.to_dict(
            only=("id", "user_id", "name_bot", "text"))})


class ReviewListResource(Resource):
    def get(self):
        session = db_session.create_session()
        rew = session.query(Reviwes).all()
        return jsonify({'Reviews': [item.to_dict(
            only=("id", "user_id", "name_bot", "text")) for item in rew]})
