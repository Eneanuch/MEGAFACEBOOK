from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    text = StringField('Что нового?', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')
