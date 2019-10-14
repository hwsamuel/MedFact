from textblob import TextBlob
from nltk import word_tokenize
from string import punctuation

'''
Represents articles returned from Trip search

title (str)		- Title of article
body (str)		- Abstract/summary of article if available
category (str)	- Evidence category of title based on Trip's evidence pyramid https://blog.tripdatabase.com/2017/10/27/sources-searched-by-trip/\
weight (int)	- Ranked arbitrary weight assigned to evidence category
source (str)	- The name of the journal or website where the article is from
year (str)		- Year the article was published
url (str)		- A link to the article (in some cases would provide full text access)
'''
class Article():
	def __init__(self, title, body, category, weight, source, year, url):
		self.title = title
		self.body = body
		self.category = category
		self.weight = weight
		self.source = source
		self.year = year
		self.url = url

	def extract(self, keywords, threshold = 3):
		"""
		Extracts the relevant phrases to use for comparison with an incoming query for computing veracity

		keywords (list)	- Query of keywords
		threshold (int)	- Returns the last-n sentences (-1 for all sentences)
		return (list)	- List of phrases and sentences to use for veracity computation
		"""
		
		sentences = TextBlob(self.body).sentences # Extract sentences from article body
		relevant = []
		for sentence in sentences:
			sentence = str(sentence).lower().strip()
			tokens = word_tokenize(sentence)
			tokens = [t.lower() for t in tokens if t not in punctuation]

			common = [value for value in keywords if value in tokens]
			if len(common) > 0: relevant.append(' '.join(tokens))

		if threshold == -1: return relevant
		else: return relevant[-threshold:]