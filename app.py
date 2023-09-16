from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

#create flask instance
app = Flask(__name__)

app.config['SECRET_KEY'] = "wwqrxqqqry"

#create form class 
class NamerForm(FlaskForm):
	name = StringField("What's your name", validators = [DataRequired()])
	submit = SubmitField("Submit")


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
	form = NamerForm()
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



