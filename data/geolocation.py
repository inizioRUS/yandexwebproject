import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class GeoLocation(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'geolocation'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    geo = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    create_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
