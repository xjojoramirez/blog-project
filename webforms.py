from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField

# Create a Search Form.
class SearchForm(FlaskForm):
	searched = StringField("Search", validators=[DataRequired()])
	submit = SubmitField("Submit")

# Create Login Form
class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")
	
#Create a Post Form
class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	# content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	content = CKEditorField('Content', validators=[DataRequired()])
	# author = StringField("Author")
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField("Submit")
	
#create form class 
class UserForm(FlaskForm):
	name = StringField("Name", validators = [DataRequired()])
	username = StringField("Username", validators = [DataRequired()])
	email = StringField("Email", validators = [DataRequired()])
	hobby = StringField("Hobby")
	submit = SubmitField("Submit")
	passw_hash = PasswordField('Password', validators = [DataRequired(), EqualTo('passw_hash2', message='Password must be identical!')]) 
	passw_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])


class PasswordForm(FlaskForm):
	email = StringField("What's your Email", validators=[DataRequired()])
	password_hash = PasswordField("What's your Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

class NamerForm(FlaskForm):
	name = StringField("What's your name:", validators=[DataRequired()])
	submit = SubmitField("Submit")