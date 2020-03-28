import datetime
import sqlalchemy


from .db_session import SqlAlchemyBase


class Ideas(SqlAlchemyBase):
    __tablename__ = 'ideas'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    idea = sqlalchemy.Column(sqlalchemy.String, nullable=True)
