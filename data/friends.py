import sqlalchemy
import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Friends(SqlAlchemyBase):
    __tablename__ = 'Friends'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    from_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    to_user = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    accepted = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
    hided = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
    date = sqlalchemy.Column(sqlalchemy.DateTime,
                             default=datetime.datetime.now)

    def __repr__(self):
        return f"<Friends> {self.id} {self.from_user} {self.to_user} {self.accepted} {self.hided} {self.date}"
