from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired, DataRequired

class SignupForm(FlaskForm):
    username= StringField('username', validators=[InputRequired()])
    firstname= StringField('firstname', validators=[InputRequired()])
    lastname= StringField('lastname', validators=[InputRequired()])
    password= StringField('password', validators=[InputRequired()])
    profpic= StringField('profpic', validators=[InputRequired()])
    genre_rate= IntegerField('genre_rate', validators=[InputRequired()])
    cast_rate= IntegerField('cast_rate', validators=[InputRequired()])
    age_rate= IntegerField('age_rate', validators=[InputRequired()])
    genre1= IntegerField('genre1', validators=[InputRequired()])
    genre2= IntegerField('genre2', validators=[InputRequired()])


class LoginForm(FlaskForm):
	username= StringField('username', validators=[InputRequired()])
	password= StringField('password', validators=[InputRequired()])


class MovieSearch(FlaskForm):
	searchterm= StringField('searchterm')