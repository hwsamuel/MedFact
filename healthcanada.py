from requests import get
from lxml import html
from lxml.html.soupparser import fromstring
from enum import Enum 
from datetime import datetime

from article import *
from pyramid import *

'''
Search field options in Trip
'''
class SearchField(Enum):
	anywhere = ''
	title = 'title_t'
	url = 'url_t'
	body = 'body_t'

'''
Queries the Health Canada search engine on specified query and fields

keywords (list) 	- Python list of keywords
field (SearchField) - Field to search

return (Article)	- List of Article objects containing matches with title, evidence category, evidence weight, source, year published, and url
'''

def query(keywords):
	source = "Health Canada"
	category_id = 18
	category = EvidencePyramid().category_map(category_id)
	weight = category[1]
	category = category[0]

	keywords = " ".join(keywords)
	base = 'https://www.canada.ca/en/sr/srb/sra.html'

	end_point = "%s?_charset_=UTF-8&fqocct=%s&allq=%s" % (base, SearchField.title.value, keywords)
	response = get(end_point)
	
	tree = html.fromstring(response.text)
	matches = tree.xpath("//article")

	results = []
	for match in matches:
		title = match.xpath(".//h3/a/text()")[0].strip()
		url = match.xpath(".//p/span[@class='text-success']/text()")[0].strip()
		date = match.xpath(".//p[2]/text()")[0].strip()
		year = datetime.strptime(date, '%b %d, %Y').year

		results.append(Article(title, category, weight, source, year, url))

	return results

'''
Unit tests
'''
def test():
	results = query(["apricot", "cancer"])
	for result in results:
		print result.title, result.category, result.weight, result.source, result.year, result.url
		print

'''
Main execution point
'''
if __name__ == '__main__':
	test()