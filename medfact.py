import sys
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from enum import Enum 

import medclass
import trip
import healthcanada
import readability
import accordcnn

REGISTERED = {
	"admin": "A98xC2qALFKD" # Regenerate pair for live/production deployment
}

""" Label to assign based on veracity and confidence"""
class TriageLabel(Enum):
	Trusted = "Trusted"
	Unknown = "Unknown"
	Untrusted = "Untrusted"

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.route('/api/', methods=['GET'])
@auth.login_required
def api():
	missing_err = "Provide text to analyze via <b>?text=</b>"
	if not request.args.get('text'): return missing_err
	
	sentence = request.args.get('text').strip().encode('utf-8')
	if sentence == '': return missing_err
	
	v_score, c_score, t_label = compute(sentence)
	fk, gf, dc, fk_label, gf_label, dc_label = readability.metrics(sentence)

	result = '[\n'
	
	result += '\t{"Trust":\n'
	result += '\t\t{\n'
	result += '\t\t\t"Veracity": '+str(v_score)+',\n'
	result += '\t\t\t"Confidence": '+str(c_score)+',\n'
	result += '\t\t\t"Triage": "'+str(t_label)+'"\n'
	result += '\t\t}\n'
	result += '\t},\n'
	
	result += '\t{"Readability":\n'
	result += '\t\t{\n'
	result += '\t\t\t"Flesch-Kincaid": {"Score": '+str(fk)+', "Label": "'+str(fk_label)+'"},\n'
	result += '\t\t\t"Gunning Fog": {"Score": '+str(gf)+', "Label": "'+str(gf_label)+'"},\n'
	result += '\t\t\t"Dale-Chall": {"Score": '+str(dc)+', "Label": "'+str(dc_label)+'"}\n'
	result += '\t\t}\n'
	result += '\t}\n'
	
	result += ']'
	
	return result

@auth.get_password
def get_pwd(username):
	if username in REGISTERED: return REGISTERED.get(username)
	else: return None

"""
Computes veracity score of a sentence using given related medical articles
For paragraphs with multiple sentences, split per sentence and aggregate score for all sentences in paragraph

sentence (str)		- Original incoming sentence to validate
return (float)		- Veracity score of incomingsentence
"""
def compute(sentence):
	medwords = medclass.predict(sentence, medical=True) # Identify medical keywords per sentence
	medwords = [m[0] for m in medwords] # Filter only the medical keywords, not the labels

	articles = healthcanada.query(medwords) # Get related articles using medical keywords

	medsentences = []
	confidence = 0
	num_articles = 0
	for article in articles:
		medfacts = article.extract(medwords)

		if len(medfacts) == 0: continue
		
		medsentences.extend(medfacts)
		confidence += article.weight
		num_articles += 1
	
	confidence = confidence/(num_articles * 23.) # Normalized with max weight of 23 for Systematic Reviews
	
	veracity = 0
	for medsentence in medsentences:
		veracity += accordcnn.predict(sentence, medsentence)
	
	veracity = (veracity * 1.)/len(medsentences)
	
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

"""
Bulk processing of paragraph containing multiple sentences or websites with multiple pages
"""
def bulk():
	return

""" Workflow example """
def example():
	sentence = "A lot of government-published studies show vaccines cause autism"
	v_score, c_score, t_label = compute(sentence)

	print 'Veracity', v_score
	print 'Confidence', c_score
	print 'Triage', t_label

if __name__ == "__main__":
	if len(sys.argv) == 2 and sys.argv[1].strip() == 'api': app.run(host='0.0.0.0',debug=False,threaded=True) # Serve RESTful API
	example()