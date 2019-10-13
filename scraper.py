from urllib import urlopen
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
	tokens = findall('\s+', sentence)
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
	html = urlopen(url)
	bs = BeautifulSoup(html.read(), 'html.parser')
	texts = bs.html.body.text
	sections = TextBlob(texts).sentences
	
	readable = ''
	for section in sections:
		section = str(section).decode('utf-8').strip()
		if check_spaces(section) and section[-1] == '.': readable += section + ' '
	return readable