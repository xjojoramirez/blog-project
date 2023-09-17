from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#create flask instance
app = Flask(__name__)
#add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#sample secret key
app.config['SECRET_KEY'] = "wwqrxqqqry"

#initialize db
db = SQLAlchemy(app)

app.app_context().push()

#create model
class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	#create a string
	def __repr__(self):
		return '<Name %r>' % self.name

#create form class 
class UserForm(FlaskForm):
	name = StringField("Name", validators = [DataRequired()])
	email = StringField("Email", validators = [DataRequired()])
	submit = SubmitField("Submit")



@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			user = Users(name=form.name.data, email=form.email.data)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.email.data = ''
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



