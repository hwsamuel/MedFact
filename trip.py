import requests, json
from xml.etree import ElementTree
from datetime import datetime
from enum import Enum 

from settings import *

class SortResults(Enum):
    quality = ''
    date = 'y'
    relevance = 't'
    popularity = 'v12m'

class SearchField(Enum):
	title = 'title:'
	anywhere = ''

def query(keywords, proximity=20):
	query = '%s"%s"~%s' % (SearchField.anywhere.value, keywords, proximity)
	
	end_point = 'https://www.tripdatabase.com/search/xml'
	data = {'criteria': query, 'key': TRIPWEB_KEY, 'sort': SortResults.quality.value}
	response = requests.get(end_point, data=data)
	
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

		results.append([title, category, weight, source, year, url])
	return results

def category_map(category_id):
	label = None
	weight = None
	
	if category_id == 11:
		label = "Systematic Reviews"
		weight = 1
	elif category_id == 1:
		label = "Evidence-Based Synopses"
		weight = 2
	elif category_id in [16,18,10,9,4]:
		label = "Clinical Guidelines"
		weight = 3
	elif category_id == 34:
		label = "Regulatory Guidance"
		weight = 4
	elif category_id == 13:
		label = "Key Primary Research"
		weight = 5
	elif category_id == 2:
		label = "Clinical Q&A"
		weight = 6
	elif category_id == 27:
		label = "Controlled Trials"
		weight = 7
	elif category_id == 14:
		label = "Primary Research"
		weight = 8
	elif category_id == 35:
		label = "Ongoing Systematic Reviews"
		weight = 9
	elif category_id == 30:
		label = "Ongoing Clinical Trials"
		weight = 10
	elif category_id == 31:
		label = "Open Controlled Trials"
		weight = 11
	elif category_id == 32:
		label = "Closed Controlled Trials"
		weight = 12
	elif category_id == 33:
		label = "Unknown Controlled Trials"
		weight = 13
	elif category_id == 22:
		label = "Patient Decision Aids"
		weight = 14
	elif category_id == 8:
		label = "Patient Information Leaflets"
		weight = 15
	elif category_id == 29:
		label = "Blogs"
		weight = 16
	elif category_id == 5:
		label = "eTextbooks"
		weight = 17
	elif category_id in [26, 21]:
		label = "Education"
		weight = 18
	
	return (label, weight)

def test():
	results = query("apricot cancer")
	for result in results:
		print result

if __name__ == '__main__':
	test()