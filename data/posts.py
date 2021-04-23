import sqlalchemy
import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Posts(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime,
                             default=datetime.datetime.now)
    posts = orm.relation("Posts", back_populates='user')
