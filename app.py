from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
	mountains = ['everest','k2','k3']
	return render_template('index.html', mountain=mountains)

@app.route('/mountains/<mt>')
def mountain(mt):
	return "This is " + str(mt)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
