from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, FloatField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from .models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[Length(max=20)])
    address = StringField('Address', validators=[Length(max=200)])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered')


class CommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Post Comment')


class BookingForm(FlaskForm):
    quantity = IntegerField('Number of Tickets', validators=[DataRequired()])
    submit = SubmitField('Book Now')


class CreateEventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=2000)])
    category = SelectField('Category', choices=[
        ('Music', 'Music'),
        ('Sports', 'Sports'),
        ('Workshop', 'Workshop'),
        ('Networking', 'Networking'),
        ('Conference', 'Conference'),
        ('Social', 'Social'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    date = DateTimeField('Event Date & Time', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    price = FloatField('Price per Ticket', validators=[DataRequired()])
    tickets_available = IntegerField('Number of Tickets', validators=[DataRequired()])
    image = StringField('Image URL (optional)', validators=[Length(max=200)])
    
    acknowledgement_type = SelectField('Acknowledgement of Country', choices=[
        ('None', 'No Acknowledgement'),
        ('Generic', 'Generic Acknowledgement'),
        ('Enhanced', 'Enhanced Acknowledgement (with research)')
    ], validators=[DataRequired()])
    
    acknowledgement_location = StringField('Event Location (for identifying Traditional Custodians)', validators=[Length(max=100)])
    acknowledgement_text = TextAreaField('Acknowledgement Statement', validators=[Length(max=1000)])
    
    submit = SubmitField('Create Event')
