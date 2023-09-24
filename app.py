from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

#create flask instance
app = Flask(__name__)
#add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#sample secret key
app.config['SECRET_KEY'] = "wwqrxqqqry"

#initialize db
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.app_context().push()

# Flask_login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))
	

# Create Login Form
class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")
# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# check the hash
			if check_password_hash(user.passw_hash, form.password.data):
				login_user(user)
				flash("Login Succesful")
				return redirect(url_for('dashboard'))
			else:
				flash("Error loggin in!")
		else:
			flash("User doesnt exist!")

	return render_template('login.html', form=form)

# create logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You have been logged out!")
	return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	form = LoginForm()
	return render_template('dashboard.html')

#Create a Blog Post model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255))
	content = db.Column(db.Text)
	author = db.Column(db.String(255))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255))

#Create a Post Form
class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	author = StringField("Author", validators=[DataRequired()])
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField("Submit")

@app.route('/posts')
def posts():
	# Grab all the posts from db
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts = posts)

#Add Post Page
@app.route('/add-post',methods=['GET', 'POST'])
@login_required
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		post = Posts(
			title = form.title.data,
			content = form.content.data,
			author = form.author.data,
			slug = form.slug.data
		)
		#clear the form
		form.title.data = ''
		form.content.data = ''
		form.author.data = ''
		form.slug.data = ''

		#Add post data to database
		db.session.add(post)
		db.session.commit()

		# return a message
		flash("Blog Post Submitted Successfully!")

	#redirect to the webpage
	return render_template("add_post.html", form=form)

# create individual post page
@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id) 
	return render_template('post.html', post=post)

# create edit post page
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id) 
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data

		# Update db
		db.session.add(post)
		db.session.commit()
		flash("Post Has Been Update!")

		return redirect(url_for('post', id=post.id))
	
	form.title.data = post.title
	form.author.data = post.author
	form.slug.data = post.slug
	form.content.data = post.content

	return render_template('edit_post.html', form=form)

# delete post
@app.route('/posts/delete/<int:id>', methods =['GET', 'POST'])
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)

	try:	
		db.session.delete(post_to_delete)
		db.session.commit()

		flash("Blog post deleted!")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts = posts)
	except:
		flash("Error deleting post!")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts = posts)

# JSON Thing
@app.route('/date')
def get_current_date():
	return {"Date":date.today()}




#create model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	
	username = db.Column(db.String(20), nullable=False, unique=True, name='unique_username_constraint')

	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True, name='unique_email_constraint')
	hobby = db.Column(db.String(100))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	#passw stuff!
	passw_hash = db.Column(db.String(128))

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute!')
	
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)
	
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	#create a string
	def __repr__(self):
		return '<Name %r>' % self.name
	

#delete
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	our_users = Users.query.order_by(Users.date_added)
	name = None
	form = UserForm()
	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("User deleted successfully!")
		return render_template('add_user.html', 
			form = form,
			name = name,
			our_users=our_users)
	except:
		flash("Error deleting user!")
		return render_template('add_user.html', 
			form = form,
			name = name,
			our_users=our_users)
	
#create form class 
class UserForm(FlaskForm):
	name = StringField("Name", validators = [DataRequired()])
	username = StringField("Username", validators = [DataRequired()])
	email = StringField("Email", validators = [DataRequired()])
	hobby = StringField("Hobby")
	submit = SubmitField("Submit")
	passw_hash = PasswordField('Password', validators = [DataRequired(), EqualTo('passw_hash2', message='Password must be identical!')]) 
	passw_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])

#update db record
@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.hobby = request.form['hobby']
		try:
			db.session.commit() 
			flash("User updated successfully!")
			return render_template("update.html", 
				form=form, 
				name_to_update=name_to_update)
		except:
			flash("Error updating the record!")
			return render_template("update.html", 
				form=form, 
				name_to_update=name_to_update)
	else:
		return render_template("update.html", 
				form=form, 
				name_to_update=name_to_update,
				id=id)

class PasswordForm(FlaskForm):
	email = StringField("What's your Email", validators=[DataRequired()])
	password_hash = PasswordField("What's your Password", validators=[DataRequired()])
	submit = SubmitField("Submit")


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			# hash passw!
			hashed_pw = generate_password_hash(form.passw_hash.data, "sha256")
			user = Users(username=form.username.data,
						name=form.name.data, 
						email=form.email.data, 
						hobby=form.hobby.data, 
						passw_hash = hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.username.data = ''
		form.email.data = ''
		form.hobby.data = ''
		form.passw_hash = ''
		flash('User added successfully!')
	our_users = Users.query.order_by(Users.date_added)
	return render_template('add_user.html', 
			form = form,
			name = name,
			our_users=our_users)


@app.route('/')
def index():
	mountains = ['everest','k2','k3']
	return render_template('index.html', mountain=mountains)

@app.route('/mountain/<mt>')
def mountain(mt):
	return "This is " + str(mt)

@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name=name)


#Custom error pages

#invalid URL
@app.errorhandler(404)
def page_not_found(error):
	return render_template("404.html"), 404

#internal server error
@app.errorhandler(500)
def page_not_found(error):
	return render_template('500.html'), 500

#create password test
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None

	form = PasswordForm()
	#validate
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		form.email.data = ''
		form.password_hash.data = ''
		
		#lookup user by email
		pw_to_check = Users.query.filter_by(email=email).first()
		
		# check hashed passw
		passed = check_password_hash(pw_to_check.passw_hash, password)


	return render_template('test_pw.html',
		email = email,
		password = password,
		pw_to_check = pw_to_check,
		passed = passed,
		form = form)


#create name page
@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = UserForm()
	#validate
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form submitted succesfully")

	return render_template('name.html',
		name = name,
		form = form)



if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)



