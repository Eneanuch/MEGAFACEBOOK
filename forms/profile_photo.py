from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileField
from wtforms import SubmitField


class PhotoForm(FlaskForm):
    photo = FileField('Аватарка', validators=[FileRequired()])
    submit = SubmitField('Изменить аватарку')
