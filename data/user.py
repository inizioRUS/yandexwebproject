import sqlalchemy
import os
import hashlib
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    surname = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    age = sqlalchemy.Column(sqlalchemy.Integer)
    gender = sqlalchemy.Column(sqlalchemy.String)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    vk_url = sqlalchemy.Column(sqlalchemy.String)
    data_reg = sqlalchemy.Column(sqlalchemy.DateTime)
    newss = orm.relation("News", back_populates='user')
    reviewss = orm.relation("Reviwes", back_populates='user')

    def set_password(self, password):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000)
        storage = salt + key
        self.hashed_password = storage

    def check_password(self, password):
        salt_from_storage = self.hashed_password[:32]
        key_from_storage = self.hashed_password[32:]
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt_from_storage,
            100000
        )
        return new_key == key_from_storage
