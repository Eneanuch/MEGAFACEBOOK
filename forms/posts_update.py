from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostUpdateForm(FlaskForm):
    text = TextAreaField('Что нового?', validators=[DataRequired()])
    submit = SubmitField('Изменить')
