from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    text = StringField('Что нового?', validators=[DataRequired()])
    photo = FileField('Аватарка', validators=[FileRequired()])
    submit = SubmitField('Опубликовать')
