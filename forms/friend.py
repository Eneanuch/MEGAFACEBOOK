from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class FriendForm(FlaskForm):
    name = StringField('Введите любые данные пользователя (имя, фамилия, город)', validators=[DataRequired()])
    submit = SubmitField('Найти')
