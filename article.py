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

	def extract(query, articles):
		"""
		Extracts the relevant phrases to use for comparison with an incoming query for computing veracity

		query (list)	- Query of keywords
		articles (list)	- List of articles
		return (list)	- List of phrases and sentences to use for veracity computation
		"""
		
		# extract sentences from article body
		# in each sentence, find the ones that have the most of keywords
		return

