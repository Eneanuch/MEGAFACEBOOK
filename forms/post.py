from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    text = TextAreaField('Что нового?', validators=[DataRequired()])
    photo = FileField('Аватарка', validators=[FileRequired()])
    submit = SubmitField('Опубликовать')
