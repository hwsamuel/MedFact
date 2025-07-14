from requests import get
from lxml import html
from lxml.html.soupparser import fromstring
from enum import Enum 
from datetime import datetime

from article import *
from pyramid import *
from scraper import *

class SearchField(Enum):
	"""
	Search field options

	>>> SearchField.title.value
	'title_t'
	>>> SearchField.url.value
	'url_t'
	>>> SearchField.body.value
	'body_t'
	>>> SearchField.anywhere.value
	''
	"""
	anywhere = ''
	title = 'title_t'
	url = 'url_t'
	body = 'body_t'

def query(keywords, field=SearchField.title.value):
	"""
	Queries the Health Canada search engine on specified query and fields

	keywords (list) 	- Python list of keywords
	field (SearchField) - Field to search
	return (Article)	- List of Article objects containing matches with title, evidence category, evidence weight, source, year published, and url

	>>> results = query(['apricot', 'cancer'])
	>>> [len(r.title) > 0 for r in results]
	[True, True, True, True, True, True]
	>>> results = query(['apricot', 'cancer'])
	>>> len(results[0].body) > 0
	True
	"""
	source = "Health Canada"
	category_id = 18
	category = EvidencePyramid().category_map(category_id)
	weight = category[1]
	category = category[0]

	keywords = " ".join(keywords).lower().strip()
	base = 'https://www.canada.ca/en/sr/srb/sra.html'

	end_point = "%s?_charset_=UTF-8&fqocct=%s&allq=%s" % (base, field, keywords)
	response = get(end_point)
	
	results = []
	try:
		tree = html.fromstring(response.text)
		matches = tree.xpath("//article")
	except:
		return results

	for match in matches:
		title = match.xpath(".//h3/a/text()")[0].strip()
		url = match.xpath(".//p/span[@class='text-success']/text()")[0].strip()
		date = match.xpath(".//p[2]/text()")[0].strip()
		if date == '' or date is None: year = ''
		else: year = datetime.strptime(date, '%b %d, %Y').year
		body = get_body(url)

		results.append(Article(title, body, category, weight, source, year, url))
	return results

""" Workflow example """
def example():
	keywords = ["apricot", "cancer"]
	results = query(keywords)
	for result in results:
		print(result.title, result.body, result.category, result.weight, result.source, result.year, result.url)
		print(result.extract(keywords))
		print()

if __name__ == '__main__':
	import doctest
	doctest.testmod() # To review doctest results, use python healthcanada.py -v
	example()