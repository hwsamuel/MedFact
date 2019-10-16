from requests import get
from xml.etree import ElementTree
from datetime import datetime
from enum import Enum 
from nltk.stem import PorterStemmer
from nltk import word_tokenize

from article import *
from pyramid import *
from scraper import *

import numpy as np

TRIPWEB_KEY = ''

""" Sorting options in Trip """
class SortResults(Enum):
    quality = '' # Default value based on best NDCG results (arbitrary)
    date = 'y'
    relevance = 't'
    popularity = 'v12m'

""" Search field options in Trip """
class SearchField(Enum):
	title = 'title:'
	anywhere = ''

'''
Queries the Trip database's web service based on specified query and fields and returns results based on sort order

keywords (list) 	- Python list of keywords
proximity (int) 	- Distance between keywords (PRO account on TRIP required)
field (SearchField) - Field to search
sorter (SortResults)- Sort order
max (int)			- Number of articles to return

return (Article)	- List of Article objects containing matches with title, evidence category, evidence weight, source, year published, and url
'''
def query(keywords, proximity=10, field=SearchField.anywhere.value, sorter=SortResults.quality.value, max=10):
	keywords = " ".join(keywords).lower()
	query = '%s"%s"~%s' % (field, keywords, proximity)
	
	end_point = 'https://www.tripdatabase.com/search/xml'
	data = {'criteria': query, 'key': TRIPWEB_KEY, 'sort': sorter, 'max': max}
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
		body = get_body(url)

		results.append(Article(title, body, category, weight, source, year, url))
	return results

""" NDCG arbitary tests to select best sorting method from TRIP results """
def ndcg():
	keywords = ["autism", "vaccinations"] # Search query keywords
	
	# Inner function to compute NDCG at k (code from https://gist.github.com/bwhite/3726239)
	def ndcg_at_k(r, k, method=0):
	    dcg_max = dcg_at_k(sorted(r, reverse=True), k, method)
	    if not dcg_max:
	        return 0.
	    return dcg_at_k(r, k, method) / dcg_max

    # Inner helper function to compute DCG at k (code from https://gist.github.com/bwhite/3726239)
	def dcg_at_k(r, k, method=0):
		r = np.asfarray(r)[:k]
		if r.size:
		    if method == 0:
		        return r[0] + np.sum(r[1:] / np.log2(np.arange(2, r.size + 1)))
		    elif method == 1:
		        return np.sum(r / np.log2(np.arange(2, r.size + 2)))
		    else:
		        raise ValueError()
		return 0.

	# Inner function to score query results by keyword hits
	def scores(matches):
		porter = PorterStemmer()
		result = []
		for match in matches:
			title_stems = [porter.stem(t.lower()) for t in word_tokenize(match.title)]
			keyword_stems = [porter.stem(k.lower()) for k in keywords]
			common = len(list(set(title_stems) & set(keyword_stems)) )
			result.append(common)
		return result
	
	# Queries TRIP and computes score for results based on different sorting orders
	r1 = scores(query(keywords, field=SearchField.anywhere.value, sorter=SortResults.quality.value))
	r2 = scores(query(keywords, field=SearchField.anywhere.value, sorter=SortResults.relevance.value))
	r3 = scores(query(keywords, field=SearchField.anywhere.value, sorter=SortResults.date.value))
	r4 = scores(query(keywords, field=SearchField.anywhere.value, sorter=SortResults.popularity.value))

	# Prints results for comparison
	print 'Quality', ndcg_at_k(r1, 5)
	print 'Relevance', ndcg_at_k(r2, 5)
	print 'Date', ndcg_at_k(r3, 5)
	print 'Popularity', ndcg_at_k(r4, 5)

""" Workflow example """
def example():
	keywords = ["vaccines", "cause", "autism"]
	results = query(keywords)
	for result in results:
		print result.title, result.body, result.category, result.weight, result.source, result.year, result.url
		print result.extract(keywords)
		print

if __name__ == '__main__':
	example()