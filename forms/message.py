from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class MessageForm(FlaskForm):
    message = StringField('Сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')