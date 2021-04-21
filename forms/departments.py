from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField


class NewsForm(FlaskForm):
    title = StringField('Название департамента', validators=[DataRequired()])
    chief = StringField('Глава департамента', validators=[DataRequired()])
    members = StringField('Члены', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    submit = SubmitField('Применить')
