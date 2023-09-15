from flask import Flask, render_template

app = Flask(__name__)

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




if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)



