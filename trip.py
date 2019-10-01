from requests import get
from xml.etree import ElementTree
from datetime import datetime
from enum import Enum 

from settings import *
from article import *
from pyramid import *

'''
Sorting options in Trip
'''
class SortResults(Enum):
    quality = ''
    date = 'y'
    relevance = 't'
    popularity = 'v12m'

'''
Search field options in Trip
'''
class SearchField(Enum):
	title = 'title:'
	anywhere = ''

'''
Queries the Trip database's web service based on specified query and fields and returns results based on sort order

keywords (list) 	- Python list of keywords
proximity (int) 	- Distance between keywords
field (SearchField) - Field to search
sorter (SortResults)- Sort order

return (Article)	- List of Article objects containing matches with title, evidence category, evidence weight, source, year published, and url
'''
def query(keywords, proximity=20, field=SearchField.anywhere.value, sorter=SortResults.quality.value):
	keywords = " ".join(keywords)
	query = '%s"%s"~%s' % (field, keywords, proximity)
	
	end_point = 'https://www.tripdatabase.com/search/xml'
	data = {'criteria': query, 'key': TRIPWEB_KEY, 'sort': sorter}
	response = get(end_point, data=data)
	
	results = []
	tree = ElementTree.fromstring(response.content)
	for child in tree.findall('document'):
		title = child.find('title').text.strip()
		category_id = int(child.find('categoryid').text)
		source = child.find('publication').text.strip()
		date = child.find('pubDate').text.strip()
		url = child.find('link').text.strip()
		
		category = EvidencePyramid().category_map(category_id)
		weight = category[1]
		category = category[0]
		year = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S GMT').year

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