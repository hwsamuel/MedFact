from urllib.request import urlopen
from bs4 import BeautifulSoup
from textblob import TextBlob
from re import findall

def check_spaces(sentence, tolerance=2):
	""" 
	Heuristic for checking number of spaces to filter out scraped menu items and other site structure contents
	Original code https://stackoverflow.com/a/34460986/863923

	sentence (str)		- Sentence to inspect
	tolerance (int)		- (Optional) Number of spaces within normal sentences
	return (bool)		- True if sentence does not exceed tolerant number of spaces else False
	"""
	tokens = findall(r'\s+', sentence)
	for i in range(0, len(tokens)):
		if len(tokens[i]) > tolerance: return False
	return True

""" Original source https://stackoverflow.com/a/1983219/863923 """
def get_body(url):
	"""
	Returns an article's full text

	url (str)		- URL of article's full text
	return (str)	- Full text of article
	"""
	readable = ''
	html = urlopen(url)
	try:
		bs = BeautifulSoup(html.read(), 'lxml')
		texts = bs.html.body.text
	except:
		return readable

	sections = TextBlob(texts).sentences
	for section in sections:
		section = str(section).strip()
		if len(section) == 0: continue
		if check_spaces(section) and section[-1] == '.': readable += section + ' '
	return readable