import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Ideas(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'ideas'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    idea = sqlalchemy.Column(sqlalchemy.String, nullable=True)
