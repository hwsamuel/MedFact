from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from xml.dom import minidom
from requests import get
from json import loads
from pickle import load, dump
from time import sleep

MSSE_KEY = '' # Register for key on StackApps and use the public key https://stackapps.com
MSSE_QUESTIONS = 'datasets/medsciences_stackexchange/posts_questions.pickle'
MSSE_LINKED = 'datasets/medsciences_stackexchange/linked_questions.pickle'
MSSE_BASE = 'https://api.stackexchange.com/2.2/questions'

"""
Gets data from Medical Sciences Stack Exchange (MSSE) via the Stack Exchange API and saves to pickle file https://api.stackexchange.com/docs/questions

from_cache (bool)	- Retrieve questions from pickle file instead of live querying via API
return (list)		- List of questions
"""
def msse_questions(from_cache = True):
	if from_cache: return load(open(MSSE_QUESTIONS, 'rb'))

	page = 1
	has_more = True
	all_posts = []

	while has_more == True:
		end_point = '%s?site=medicalsciences&pagesize=100&page=%s&key=%s' % (MSSE_BASE, page, MSSE_KEY)
		response = get(end_point)
		posts = loads(response.content)
		has_more = posts['has_more']
		all_posts.extend(posts['items'])
		page += 1

	dump(all_posts, open(MSSE_CACHE, 'wb'))
	return all_posts

"""
Get all linked questions on Medical Sciences Stack Exchange and saves to pickle file https://api.stackexchange.com/docs/linked-questions

posts (list)	- (Optional) If posts specified, then queries API to get linked pairs, else returns cached pairs from pickle file
return (list)	- Linked question pair titles and ids as pickle file (id1, id2, title1, title2)
"""
def msse_linked(posts = None):
	if posts is None: return load(open(MSSE_LINKED, 'rb'))
	THROTTLE = 10

	pairs = []
	to_process = len(posts)
	count = 1
	for post in posts:
		count += 1
		if count >= THROTTLE: # Respecting API throttling https://api.stackexchange.com/docs/throttle
			count = 1
			sleep(2)
		
		id = post['question_id']
		title = post['title']
		linked_api = '%s/%s/linked?&site=medicalsciences&key=%s' % (MSSE_BASE, id, MSSE_KEY)
		response = get(linked_api)
		linked = loads(response.content)

		if len(linked['items']) == 0: continue
		for related in linked['items']:
			pairs.append((id, related['question_id'], title, related['title']))

	dump(pairs, open(MSSE_LINKED, 'wb'))
	return pairs

"""
Get unrelated question pairs from Medical Science Stack Exchange dataset

return (list)	- Pairs of question titles that are not related or duplicates (arbitrary)
"""
def msse_unlinked():
	questions = load(open(MSSE_QUESTIONS, 'rb'))
	linked = load(open(MSSE_LINKED, 'rb'))

"""
Tokenizes Health Stack Exchange dataset https://archive.org/download/stackexchange
NB - Many of the questions marked as duplicate in this dataset do not have the question title recorded and the live version also does not have the questions (probably deleted)

return (list)	- Pairs of question titles that have been marked as duplicates by moderators (title1, title2)
"""
def hse():
	links = minidom.parse('datasets/health_stackexchange/PostLinks.xml')
	rows = links.getElementsByTagName('row')
	duplicates = {}
	for row in rows:
		link_type = int(row.attributes['LinkTypeId'].value)
		if link_type != 3: continue # Reference https://ia600107.us.archive.org/27/items/stackexchange/readme.txt
		post1_id = int(row.attributes['Id'].value)
		post2_id = int(row.attributes['PostId'].value)
		duplicates[post1_id] = post2_id
	
	posts = minidom.parse('datasets/health_stackexchange/Posts.xml')
	rows = posts.getElementsByTagName('row')
	all_posts = {}
	for row in rows:
		if 'Title' not in row.attributes.keys(): continue
		post_id = int(row.attributes['Id'].value)
		post_title = row.attributes['Title'].value.encode('utf-8')
		post_tags = row.attributes['Tags'].value.encode('utf-8') if 'Tags' in row.attributes.keys() else None
		all_posts[post_id] = (post_title, post_tags)

	pairs = []
	for d in duplicates.keys():
		pair = duplicates[d]
		if d in all_posts.keys() and pair in all_posts.keys():
			pairs.append((all_posts[d][0], all_posts[pair][0]))

	return pairs

if __name__ == '__main__':
	print "Total number of questions scraped", len(msse_questions())
	print "Total number of linked questions", len(msse_linked())