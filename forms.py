from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField,IntegerField, SelectField
from wtforms.validators import InputRequired, Email, Length 
from wtforms.validators import DataRequired, Email, Length, NumberRange

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=10, max=120)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SOSForm(FlaskForm):
    phone = StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=15)])
    submit = SubmitField('Add Contact')

class ReportForm(FlaskForm):
    area = StringField('Area', validators=[DataRequired()])
    content = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit Report')
