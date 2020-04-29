from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.user import User


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'User': user.to_dict(
            only=("id", "login","data_reg"))})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'User': [item.to_dict(
            only=("id", "login","data_reg")) for item in user]})
