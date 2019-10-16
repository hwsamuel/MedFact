from textblob import TextBlob
from nltk import word_tokenize
from nltk import flatten
from string import punctuation
from enum import Enum 
from random import shuffle

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

class Sampler(Enum):
	first = 0		# Choose first-n sentences
	last = 1		# Choose last-n sentences
	random = 2		# Choose random-n sentences
	best = 3		# Choose sentences with most keyword hits

class Article():
	def __init__(self, title, body, category, weight, source, year, url):
		self.title = title
		self.body = body
		self.category = category
		self.weight = weight
		self.source = source
		self.year = year
		self.url = url

	def extract(self, keywords, threshold = 3, sampler = Sampler.last.value):
		"""
		Extracts the relevant phrases to use for comparison with an incoming query for computing veracity

		keywords (list)		- Query of keywords
		threshold (int)		- Controls number of sentences to return (-1 for all sentences)
		sampler(Sampler) 	- Returns first-n, last-n, random-n or best-n number of sentences (heuristic)

		return (list)		- List of phrases and sentences to use for veracity computation
		"""
		
		sentences = TextBlob(self.body).sentences # Extract sentences from article body
		relevant = {}
		for sentence in sentences:
			sentence = str(sentence).decode('utf-8').lower().strip()
			tokens = word_tokenize(sentence)
			tokens = [t.lower() for t in tokens if t not in punctuation]

			common = len([value for value in keywords if value in tokens])
			if common == 0: continue
			if common not in relevant.keys(): relevant[common] = []
			relevant[common].append(' '.join(tokens))

		if threshold == -1: return flatten(relevant.values())

		if sampler == Sampler.last.value:
			return flatten(relevant.values())[-threshold:]
		elif sampler == Sampler.first.value:
			return flatten(relevant.values())[:threshold]
		elif sampler == Sampler.random.value:
			shuffle(flatten(relevant.values()))
			return relevant[-threshold:]
		elif sampler == Sampler.best.value:
			result = []
			for key in sorted(relevant.keys(), reverse=True): # Sort by keyword hits
				result.extend(relevant[key])
				if len(result) >= threshold: break
			return result[:threshold]