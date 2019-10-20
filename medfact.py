import sys, sqlite3, re
from flask import Flask, flash, request, jsonify, render_template
from flask_httpauth import HTTPBasicAuth
from enum import Enum 
from textblob import TextBlob

import medclass
import readability
import scraper

BULK_THRESHOLD = 10 # Threshold for number of sentences to sample from website

REGISTERED = {
	"admin": "A98xC2qALFKD" # Regenerate pair for live/production deployment
}

""" Label to assign based on veracity and confidence """
class TriageLabel(Enum):
	Trusted = "Trusted"
	Unknown = "Unknown"
	Untrusted = "Untrusted"

""" Label for batch mode """
class BatchMode(Enum):
	Text = "text"
	URL = "url"

app = Flask(__name__)
auth = HTTPBasicAuth()
app.secret_key = 'YwycT897iWAr' # For session management, regenerate for live server

@app.route('/api/gui/submit', methods=['POST'])
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
 		if text_size > 1000: 
 			flash("Text is too long", 'danger')
 			err = True
 		elif text_size < 3: 
 			flash("Text is too short", 'danger')
 			err = True
	elif mode == BatchMode.URL.value:
		num_urls = len(content.split('\n'))
 		valid_urls = content.count('http')
		if num_urls > 100: 
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

@app.route('/api/gui/', methods=['GET'])
@auth.login_required
def gui():
	return render_template('gui.html')

@app.route('/api/text/', methods=['GET'])
@auth.login_required
def api_text():
	missing_err = "Provide text to analyze via <b>?text=</b>"
	if not request.args.get('text'): return missing_err
	
	sentence = request.args.get('text').strip().decode('utf-8')
	if sentence == '': return missing_err

	v_score, c_score, t_label = compute(sentence)
	fk, gf, dc, fk_label, gf_label, dc_label = readability.metrics(sentence)

	return jsonify(format_json(v_score, c_score, t_label, fk, gf, dc, fk_label, gf_label, dc_label))

@app.route('/api/url/', methods=['GET'])
@auth.login_required
def api_url():
	missing_err = "Provide text to analyze via <b>?url=</b>"
	if not request.args.get('url'): return missing_err
	
	address = request.args.get('url').strip().decode('utf-8')
	if address == '': return missing_err

	text = scraper.get_body(address)
	v_score, c_score, t_label, fk, gf, dc, fk_label, gf_label, dc_label = score_sentences(text)
	return jsonify(format_json(v_score, c_score, t_label, fk, gf, dc, fk_label, gf_label, dc_label))

@auth.get_password
def get_pwd(username):
	if username in REGISTERED: return REGISTERED.get(username)
	else: return None

"""
Score corpus containing multiple sentences 
text (str)		- Paragraph containing sentences
return (json)	- Trust and readability scores
"""
def score_sentences(text):
	sentences = TextBlob(text).sentences
	v_score = 0
	c_score = 0
	count = 0
	fk = 0
	gf = 0
	dc = 0
	for sentence in sentences:
		if count > BULK_THRESHOLD: break

		sentence = str(sentence).decode('utf-8')
		
		medwords = medclass.predict(sentence, medical=True)
		if medwords == []: continue
		
		v, c, l = compute(sentence, medwords)
		fk1, gf1, dc1, l1, l2, l3 = readability.metrics(sentence)

		if v == -1: continue
		v_score += v
		c_score += c
		count += 1

		fk += fk1
		gf += gf1
		dc += dc1
	
	v_score = round((v_score*1.)/count, 3)
	c_score = round((c_score*1.)/count, 3)
	t_label = triage(v_score, c_score)

	fk_label = readability.grade_label(round(fk))
	gf_label = readability.grade_label(round(gf))
	dc_label = readability.grade_label(round(dc))

	return (v_score, c_score, t_label, fk, gf, dc, fk_label, gf_label, dc_label)

""" Formats given inputs into a JSON object for API output """
def format_json(v_score, c_score, t_label, fk, gf, dc, fk_label, gf_label, dc_label):
	result = {}
	result['Trust'] = {}
	result['Readability'] = {}

	result['Trust']['Veracity'] = v_score
	result['Trust']['Confidence'] = c_score
	result['Trust']['Triage'] = t_label

	result['Readability']['Flesch-Kincaid'] = {}
	result['Readability']['GunningFog'] = {}
	result['Readability']['Dale-Chall'] = {}

	result['Readability']['Flesch-Kincaid']['Score'] = fk
	result['Readability']['Flesch-Kincaid']['Label'] = fk_label

	result['Readability']['GunningFog']['Score'] = gf
	result['Readability']['GunningFog']['Label'] = gf_label

	result['Readability']['Dale-Chall']['Score'] = dc
	result['Readability']['Dale-Chall']['Label'] = dc_label

	return result
	
"""
Computes veracity score of a sentence using given related medical articles
For paragraphs with multiple sentences, split per sentence and aggregate score for all sentences in paragraph

sentence (str)	- Original incoming sentence to validate
medwords (list)	- (Optional) List of pre-extracted medical words from sentence
return (set)	- Veracity score, confidence, and TriageLabel of incoming sentence
"""
def compute(sentence, medwords = None):
	import accordcnn
	import trip
	import healthcanada

	if medwords == None: medwords = medclass.predict(sentence, medical=True) # Identify medical keywords per sentence
	
	medwords = [m[0] for m in medwords] # Filter only the medical keywords, not the labels
	if len(medwords) < 2: return (-1, 1, TriageLabel.Unknown.value)
		
	hc_articles = healthcanada.query(medwords) # Get related articles using medical keywords
	trip_articles = trip.query(medwords)
	
	articles = hc_articles + trip_articles

	medsentences = []
	confidence = 0
	num_articles = 0
	for article in articles:
		if article.body.strip() == '': continue

		medfacts = article.extract(medwords)
		if len(medfacts) == 0: continue
		
		medsentences.extend(medfacts)
		confidence += article.weight
		num_articles += 1
	
	if num_articles > 0: 
		confidence = confidence/(num_articles * 23.) # Normalized with max weight of 23 for Systematic Reviews
	else:
		confidence = 0
	
	veracity = 0
	for medsentence in medsentences:
		veracity += accordcnn.predict(sentence, medsentence)
	
	if len(medsentences) > 0:
		veracity = (veracity * 1.)/len(medsentences)
	else:
		veracity = 0
	
	label = triage(veracity, confidence)
	
	return (round(veracity, 3), round(confidence, 3), label)

"""
Determines triage label based on confidence and veracity
veracity (float)		- Trust score
confidence (float)		- Confidence score
return (TriageLabel)	- Either Trusted, Untrusted or Unknown
"""
def triage(veracity, confidence):
	label = TriageLabel.Unknown.value

	if confidence < 0.5: # Sources lower than Primary Research on the evidence pyramid have uncertain conclusions
		return label

	if veracity >= 0.75:
		label = TriageLabel.Trusted.value
	elif veracity < 0.75 and veracity > 0.5:
		label = TriageLabel.Unknown.value
	else:
		label = TriageLabel.Untrusted.value

	return label

""" Workflow examples """
def example1():
	sentence = "A lot of government-published studies show vaccines cause autism"
	v_score, c_score, t_label = compute(sentence)

	print 'Veracity', v_score
	print 'Confidence', c_score
	print 'Triage', t_label

""" Example for bulk analysis of website's home page """
def example2():
	address = 'https://thetruthaboutcancer.com/apricot-kernels-for-cancer/'
	text = scraper.get_body(address)
	sentences = TextBlob(text).sentences

	v_score = 0
	c_score = 0
	count = 0
	for sentence in sentences:
		if count > BULK_THRESHOLD: break

		sentence = str(sentence).decode('utf-8')
		medwords = medclass.predict(sentence, medical=True)
		if medwords == []: continue

		v, c, l = compute(sentence.strip(), medwords)
		if v == -1: continue

		v_score += v
		c_score += c
		count += 1
	
	v_score = round((v_score*1.)/count, 3)
	c_score = round((c_score*1.)/count, 3)
	t_label = triage(v_score, c_score)

	print v_score, c_score, t_label

if __name__ == "__main__":
	if len(sys.argv) == 2 and sys.argv[1].strip() == 'api':
		app.run(host='0.0.0.0',debug=False,threaded=True) # Serve RESTful API
	else:
		example2()