from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    team_leader = StringField('Лидер команды', validators=[DataRequired()])
    job = TextAreaField("Содержание работы")
    work_size = StringField('Размер работы в часах', validators=[DataRequired()])
    collaborators = StringField('Список помощников', validators=[DataRequired()])
    is_finished = BooleanField('Работа закончена?')
    submit = SubmitField('Применить')
