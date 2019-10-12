import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

from gensim.models import KeyedVectors
from sklearn.feature_extraction import stop_words
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from textblob import TextBlob
from xml.dom import minidom
from requests import get
from json import loads
from pickle import load, dump
from time import sleep
from random import shuffle
import numpy as np, spacy

MSSE_KEY = '' # Register for key on StackApps and use the public key https://stackapps.com
MSSE_QUESTIONS = 'datasets/medsciences_stackexchange/posts_questions.pickle'
MSSE_LINKED = 'datasets/medsciences_stackexchange/linked_questions.pickle'
MSSE_UNLINKED = 'datasets/medsciences_stackexchange/unlinked_questions.pickle'
MSSE_ENCODED = 'datasets/medsciences_stackexchange/encoded_questions.pickle'
MODEL_NAME = 'models/accordcnn.model'
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

from_cache (bool)	- (Optional) Gets pairs from saved pickle file or recomputes
size (int)			- (Optional) Size of data to return
randomize (bool)		- (Optional) Randomizes the returned list

return (list)		- Pairs of question titles that are not related or duplicates (arbitrary)
"""
def msse_unlinked(from_cache = True, size = 500, randomize = True):
	if from_cache: 
		all_unlinked = load(open(MSSE_UNLINKED, 'rb'))
		
		if randomize: shuffle(all_unlinked)
		all_unlinked = all_unlinked[:size]	

		return all_unlinked

	questions = load(open(MSSE_QUESTIONS, 'rb'))
	linked = load(open(MSSE_LINKED, 'rb'))

	all_linked = {}
	for link in linked:
		all_linked[link[0]] = None
		all_linked[link[1]] = None

	unlinked = {}
	for question in questions:
		id = question['question_id']
		if id in all_linked.keys(): continue
		unlinked[id] = question['title']

	all_unlinked = []
	pairs = []
	for question in unlinked.values():
		if len(pairs) == 2:
			all_unlinked.append(pairs)
			pairs = []
		pairs.append(question)
	
	dump(all_unlinked, open(MSSE_UNLINKED, 'wb'))

	if randomize: shuffle(all_unlinked)
	all_unlinked = all_unlinked[:size]	

	return all_unlinked
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

''' 
Encodes a given set of vectors using Word2vec embeddings trained on PubMed and also associates class label  

tokens (str)		- Sentence to encode
return (ndarray)	- Numpy array of embeddings and associated labels
'''
spacy_model = spacy.load('en_core_web_sm')
encoder = KeyedVectors.load_word2vec_format('datasets/pubmed2018_w2v_200D.bin', binary=True) # Word2vec embeddings embeddings pre-trained on text from MEDLINE/PubMed Baseline 2018 by AUEB's NLP group http://nlp.cs.aueb.gr

def encode(sentence):
	sentence = unicode(sentence.encode('punycode'))
	clean_sentence = ''
	for token in sentence.split():
		token = token.lower()
		if token in encoder.wv: clean_sentence += token + ' '

	blob = TextBlob(sentence)
	polarity = blob.sentiment.polarity
	subjectivity = blob.sentiment.subjectivity

	negations = len([tok for tok in spacy_model(sentence) if tok.dep_ == 'neg'])
	
	encoded = encoder.wv[clean_sentence.split()]
	encoded = np.mean(encoded, axis=0)
	encoded = np.append(encoded, [polarity, subjectivity, negations])
	
	return encoded

"""
Encodes data for feeding into MLP

from_cache (bool)	- (Optional) If true, it returns previously saved cache of encoded data
return (set)		- Pairs of encoded inputs and labels
"""

def msse(from_cache = True):
	if from_cache: return load(open(MSSE_ENCODED, 'rb'))
	
	X = []
	y = []

	lnk = msse_linked()
	for l in lnk:
		X.append(encode(l[2] + ' ' + l[3]))
		y.append(1)

	ulnk = msse_unlinked()
	for l in ulnk:
		X.append(encode(l[0] + ' ' + l[1]))
		y.append(0)

	dump((X, y), open(MSSE_ENCODED, 'wb'))
	return (X, y)

"""
Train shallow CNN using Medical Sciences Stack Exchange linked questions' titles 

cache (bool)	- Specify whether to save trained model as Pickle file
return (float)	- Trained model's accuracy score
"""
def train(cache=True):
	X, y = msse()
	
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=10)

	mlp = MLPClassifier(hidden_layer_sizes=(200,), max_iter=200, alpha=1e-4, solver='sgd', verbose=10, tol=1e-4, random_state=1, learning_rate_init=.1)
	mlp.fit(X_train, y_train)

	if cache: dump(mlp, open(MODEL_NAME, 'wb'))
	return mlp.score(X_test, y_test)

'''
Predicts label for sentence pairs based on trained model loaded as a Pickle file
sentence1 (str)	- First sentence to predict label for
sentence2 (str)	- Second sentence to predict label for
return (int)	- 0 if pairs disagree or 1 if pairs agree
'''
def predict(sentence1, sentence2):
	mlp = load(open(MODEL_NAME, 'rb'))

	encodings = encode(sentence1 + ' ' + sentence2).reshape(1, -1)
	return mlp.predict(encodings)

""" Sanity test """
def test():
	print predict('Is autism an autoimmune disease?', 'Can cannabidiol help on Autism Spectrum Disorder?')
	print predict('Is autism an autoimmune disease?', "What is gerrymandering called if it's not the result of redrawing districts?")

if __name__ == '__main__':
	test()
