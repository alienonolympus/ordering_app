from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from flask_wtf.file import FileRequired, FileField, FileAllowed
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    tutor_group = StringField('Tutor Group', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired()])
    submit = SubmitField('Signup')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')

    def check_password(self, password, password2):
        if password != password2:
            raise ValidationError('Please repeat your password again')
    
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_password2 = PasswordField('Repeat New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

class NewOrderForm(FlaskForm):
    name = StringField('Order Name', validators=[DataRequired()])
    uploaded_file = FileField('Order File', validators=[FileRequired(), FileAllowed(['jpg', 'gif', 'png', 'jpeg', 'tiff'], 'Images only')])
    submit = SubmitField('Signup')
