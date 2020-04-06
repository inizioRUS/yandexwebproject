import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase

association_table = sqlalchemy.Table('association', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('News', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('News.id')),
                                     sqlalchemy.Column('Genre', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('Genre.id'))
                                     )


class Genre(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Genre'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
