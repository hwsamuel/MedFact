import sqlite3, re
from flask import Flask, flash, request, jsonify, render_template
from flask_httpauth import HTTPBasicAuth
from enum import Enum

REGISTERED = {
	"admin": "A98xC2qALFKD" # Regenerate pair for live/production deployment
}

""" Label for batch mode """
class BatchMode(Enum):
	Text = "text"
	URL = "url"

app = Flask(__name__)
auth = HTTPBasicAuth()
app.secret_key = 'YwycT897iWAr' # For session management, regenerate for live server

""" Main page for web app """
@app.route('/medfact/', methods=['GET'])
@auth.login_required
def home():
	return render_template('gui.html')

""" Page to process form submission """
@app.route('/medfact/submit/', methods=['POST'])
@auth.login_required
def submit():
	mode = request.form.get('mode').strip()
	content = request.form.get('content').strip()
	email = request.form.get('email').strip()
 
 	err = False

 	if re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email) == None:
 		flash("Invalid email provided", 'danger')
 		err = True

 	if mode == BatchMode.Text.value:
 		text_size = len(content.split())
 		if text_size > 100: 
 			flash("Text is too long", 'danger')
 			err = True
 		elif text_size < 3: 
 			flash("Text is too short", 'danger')
 			err = True
	elif mode == BatchMode.URL.value:
		num_urls = len(content.split('\n'))
 		valid_urls = content.count('http')
		if num_urls > 10: 
			flash("Too many URLs", 'danger')
			err = True
		elif num_urls < 1 or num_urls != valid_urls: 
			flash("Not enough valid URLs have been entered", 'danger')
			err = True
	else:
		flash("Invalid batch mode selected", 'danger')
		err = True

	if err == False:
		db = sqlite3.connect('batch.sqlite')
		cursor = db.cursor()
		cursor.execute("INSERT INTO jobs (mode, content, email) VALUES (?,?,?)", (mode, content, email))
		db.commit()
		db.close()
		flash('Submitted batch request successfully, results will be sent via email when processed', 'info')

	return render_template('gui.html')

@auth.get_password
def get_pwd(username):
	if username in REGISTERED: return REGISTERED.get(username)
	else: return None

if __name__ == "__main__":
	app.run(host='0.0.0.0',debug=False,threaded=True) # Serve RESTful API