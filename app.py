from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, SearchForm, NamerForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

#create flask instance
app = Flask(__name__)
# add ckeditor
ckeditor = CKEditor(app)

#add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#sample secret key
app.config['SECRET_KEY'] = "wwqrxqqqry"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
	
# Create search function
@app.route('/search', methods=["POST"])
def search():
	form = SearchForm()
	posts = Posts.query
	if form.validate_on_submit():
		# Get data from submitted form
		post.searched = form.searched.data

		# Query the database
		posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
		posts = posts.order_by(Posts.title).all()

		return render_template("search.html", 
						 form=form,
						 searched = post.searched,
						 posts = posts)
# Pass stuff to navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

# Create Admin Page
@app.route('/admin')
@login_required
def admin():
	if current_user.id == 1:
		return render_template('admin.html')
	else:
		flash("Sorry! You are not an admin.")
		return redirect(url_for('dashboard'))

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
	form = UserForm()
	id=current_user.id
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.hobby = request.form['hobby']
		name_to_update.username = request.form['username']
		name_to_update.about_author = request.form['about_author']

		# Check for profile pic
		if request.files['profile_pic']:
			name_to_update.profile_pic = request.files['profile_pic']	

			# Grab Image Name
			pic_filename = secure_filename(name_to_update.profile_pic.filename)

			# Set uuid
			pic_name = str(uuid.uuid1()) + "_" + pic_filename

			# Save image
			saver = request.files['profile_pic']
			
			# Change it to a string to save to db 
			name_to_update.profile_pic = pic_name
			
			try:
				db.session.commit() 
				saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
				flash("User updated successfully!")
				return render_template("dashboard.html", 
					form=form, 
					name_to_update = name_to_update)
			except:
				flash("Error updating the record!")
				return render_template("dashboard.html", 
					form=form, 
					name_to_update = name_to_update)
		else:
			db.session.commit() 
			flash("User updated successfully!")
			return render_template("dashboard.html",
						  form=form,
						  name_to_update = name_to_update)
	else:
		return render_template("dashboard.html", 
				form=form, 
				name_to_update = name_to_update,
				id=id)

# Create posts page
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
		poster = current_user.id
		post = Posts(
			title = form.title.data,
			content = form.content.data,
			poster_id = poster,
			slug = form.slug.data
		)
		#clear the form
		form.title.data = ''
		form.content.data = ''
		# form.author.data = ''
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
		# post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data

		# Update db
		db.session.add(post)
		db.session.commit()
		flash("Post Has Been Update!")

		return redirect(url_for('post', id=post.id))
	
	if current_user.id == post.poster_id:
		form.title.data = post.title
		# form.author.data = post.author
		form.slug.data = post.slug
		form.content.data = post.content

		return render_template('edit_post.html', form=form)
	
	else:
		flash("You can't edit this post!")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts = posts)
		
# delete post
@app.route('/posts/delete/<int:id>', methods =['GET', 'POST'])
@login_required
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	id = current_user.id

	if id == post_to_delete.poster.id or id == 1:
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
	else:
		flash("You can't delete this post!")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts = posts)
# JSON Thing
@app.route('/date')
def get_current_date():
	return {"Date":date.today()}

#delete user
@app.route('/delete/<int:id>')
@login_required
def delete(id):
	if id == current_user.id or id == 1:
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
	else:
		flash("Sorry, you can't delete this user!")
		return redirect(url_for('dashboard'))
	
#update user
@app.route('/update/<int:id>', methods = ['GET', 'POST'])
@login_required
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.hobby = request.form['hobby']
		name_to_update.username = request.form['username']
		name_to_update.about_author = request.form['username']
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



# Create add user page
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

# Custom Jinja2 filter for formatting datetime objects
@app.template_filter('datetimefilter')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    if value is None:
        return ''
    return value.strftime(format)	

# index route
@app.route('/')
def index():
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template('index.html', posts=posts)

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



#Create a Blog Post model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255))
	content = db.Column(db.Text)
	#author = db.Column(db.String(255))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255))
	# foreign key to link users (refer to primary key of the user )
	poster_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_posts_users'))


#create model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True, name='unique_username_constraint')
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True, name='unique_email_constraint')
	hobby = db.Column(db.String(100))
	about_author = db.Column(db.Text(500), nullable=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	profile_pic = db.Column(db.String(), nullable=True)

	#passw stuff!
	passw_hash = db.Column(db.String(128))

	# Users can have many posts
	posts = db.relationship('Posts', backref='poster')

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



if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)



