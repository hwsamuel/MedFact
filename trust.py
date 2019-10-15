import sys
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth

import medclass
import trip
import healthcanada
import readability

REGISTERED = {
	"admin": "A98xC2qALFKD"
}

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.route('/api/', methods=['GET'])
@auth.login_required
def api():
	missing_err = "Provide text to analyze via ?text="
	if not request.args.get('text'): return missing_err
	
	sentence = request.args.get('text').strip()
	if sentence == '': return missing_err
	
	v_score, c_score, t_label = (0, 0, 0)
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
	result += '\t\t\t"Flesch-Kincaid": {"Score": '+str(fk)+', "Label": "'+fk_label+'"},\n'
	result += '\t\t\t"Gunning Fog": {"Score": '+str(gf)+', "Label": "'+gf_label+'"},\n'
	result += '\t\t\t"Dale-Chall": {"Score": '+str(dc)+', "Label": "'+dc_label+'"}\n'
	result += '\t\t}\n'
	result += '\t}\n'
	
	result += ']'
	
	return result

@auth.get_password
def get_pwd(username):
	if username in REGISTERED: return REGISTERED.get(username)
	else: return None

def veracity(keywords, articles):
	return

def confidence(articles):
	return

def triage(veracity, confidence):
	return

def bulk(url):
	return

if __name__ == "__main__":
	if len(sys.argv) == 2 and sys.argv[1].strip() == 'api': app.run(host='0.0.0.0',debug=False,threaded=True) # Serve RESTful API

	sentences = [
		"A lot of government-published studies show vaccines cause autism.",
		"When dealing with a misbehaving child, intentionally ignore a problem behavior instead of reacting or giving negative attention to the child.",
		"ABA therapy accounts for 45% of pediatric therapies that develop long-lasting and observable results.",
		"Parents of children with disabilities should not be allowed to use growth attenuation therapy.",
		"I'm swimming up above the waves to see the sky of blue; I've never seen it even once, and now it's time I do."
	]

	for sentence in sentences:
		# todo: get med keywords from sentence
		# todo: get related articles using keywords

		v_score = veracity(keywords, articles)
		c_score = confidence(articles)
		t_label = triage(v, c)

		print sentence
		print 'Veracity', v_score
		print 'Confidence', c_score
		print 'Triage', t_label
		print