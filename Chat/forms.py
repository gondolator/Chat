from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Required
from wtforms import validators

class InputForm(FlaskForm):
    description = StringField('Eingabe')
    sektion = StringField('Sektion')
    pid = StringField('PID')
    submit = SubmitField('Senden')

class LoginForm(FlaskForm):
    Benutzername = StringField('Benutzername')
    Passwort = PasswordField('Passwort')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    Benutzername = StringField('Benutzername', [validators.required(), validators.length(min=4), validators.length(max=20)])
    Passwort = PasswordField('Passwort', [validators.required(), validators.length(min=4)])
    Passwort2 = PasswordField('Passwort')
    submit = SubmitField('Register')
