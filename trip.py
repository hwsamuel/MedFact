from requests import get
from xml.etree import ElementTree
from datetime import datetime
from enum import Enum 
from collections import OrderedDict

from settings import *

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
Mapping of numeric internal Trip values assigned for evidence categories to human-readable text
'''
class EvidencePyramid(Enum):
	categories = OrderedDict()
	categories[11] = "Systematic Reviews"
	categories[1] = "Evidence-Based Synopses"
	
	_lbl1 = "Clinical Guidelines"
	categories[16] = _lbl1
	categories[18] = _lbl1
	categories[10] = _lbl1
	categories[9] = _lbl1
	categories[4] = _lbl1
	
	categories[34] = "Regulatory Guidance"
	categories[13] = "Key Primary Research"
	categories[2] = "Clinical Q&A"
	categories[27] = "Controlled Trials"
	categories[14] = "Primary Research"
	categories[35] = "Ongoing Systematic Reviews"
	categories[30] = "Ongoing Clinical Trials"
	categories[31] = "Open Controlled Trials"
	categories[32] = "Closed Controlled Trials"
	categories[33] = "Unknown Controlled Trials"
	categories[22] = "Patient Decision Aids"
	categories[8] = "Patient Information Leaflets"
	categories[29] = "Blogs"
	categories[5] = "eTextbooks"

	_lbl2 = "Education"
	categories[26] = _lbl2
	categories[21] = _lbl2

'''
Represents articles returned from Trip search

title (str)		- Title of article
category (str)	- Evidence category of title based on Trip's evidence pyramid https://blog.tripdatabase.com/2017/10/27/sources-searched-by-trip/\
weight (int)	- Ranked arbitrary weight assigned to evidence category
source (str)	- The name of the journal or website where the article is from
url (str)		- A link to the article (in some cases would provide full text access)
'''
class Article():
	def __init__(self, title, category, weight, source, year, url):
		self.title = title
		self.category = category
		self.weight = weight
		self.source = source
		self.year = year
		self.url = url

'''
Queries the Trip database's web service based on specified query and fields and returns results based on sort order

keywords (list) 	- Python list of keywords
proximity (int) 	- Distance between keywords
field (SearchField) - Field to search
sorter (SortResults)- Sort order

return (Article)	- List of Article objects containing matches with title, evidence category, evidence weight, source, year published, and url
'''
def query(keywords, proximity=20, field=SearchField.anywhere.value, sorter=SortResults.quality.value):
	query = '%s"%s"~%s' % (field, keywords, proximity)
	
	end_point = 'https://www.tripdatabase.com/search/xml'
	data = {'criteria': query, 'key': TRIPWEB_KEY, 'sort': sorter}
	response = get(end_point, data=data)
	
	results = []
	tree = ElementTree.fromstring(response.content)
	for child in tree.findall('document'):
		title = child.find('title').text
		category_id = int(child.find('categoryid').text)
		source = child.find('publication').text
		date = child.find('pubDate').text
		url = child.find('link').text
		
		category = category_map(category_id)
		weight = category[1]
		category = category[0]
		year = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S GMT').year

		results.append(Article(title, category, weight, source, year, url))
	return results

'''
Converts Trip's category ID to human-readable text and related ranked weight

category_id (int)	- Trip ID of the category
return (set)		- Human-readable label and ranked weight of category
'''
def category_map(category_id):
	weight = len(EvidencePyramid.categories.value.keys()) - EvidencePyramid.categories.value.keys().index(category_id)
	return (EvidencePyramid.categories.value[category_id], weight)

'''
Unit tests
'''
def test():
	results = query("apricot cancer")
	for result in results:
		print result.title, result.category, result.weight, result.source, result.year, result.url
		print

'''
Main execution point
'''
if __name__ == '__main__':
	test()