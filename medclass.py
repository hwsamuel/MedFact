import warnings, nltk, numpy as np, glob, string, pickle
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

from gensim.models import KeyedVectors
from sklearn.feature_extraction import stop_words
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split

MODEL_NAME = 'models/medclass.model'

""" Tokenizes the SNOMED CT International dataset flat file """
def snomedct():
	data = open('datasets/sct2_Description_Delta-en_INT_20190731.txt', 'r') # Source (requires UMLS account) https://www.nlm.nih.gov/healthit/snomedct/international.html
	terms = []
	for line in data:
		line = line.strip().split()
		terms.append(line[7].lower())
	return terms

""" Tokenizes the Consumer Health Vocabulary dataset flat file """
def chv():
	data = open('datasets/CHV_concepts_terms_flatfile_20110204.tsv', 'r') # Source https://github.com/Planeshifter/node-chvocab
	terms = []
	for line in data:
		line = line.strip().split()
		terms.append(line[1].lower())
	return terms

""" Tokenizes Simple English Wikipedia flat text files """
def sew():
	terms = []
	path = 'datasets/simplewiki-20150406-pages-articles/*.txt' # Source http://pikes.fbk.eu/eval-sew.html
	files = glob.glob(path)
	for file in files:
		data = open(file, 'r')
		for line in data:
			tokens = tokenize(line.decode('utf-8'))
			terms.extend(tokens)
	return terms

''' 
Encodes a given set of vectors using Word2vec embeddings trained on PubMed and also associates class label  
tokens (list)	- List of tokens to encode
label (int)		- (Optional) Label to associate with set of tokens (-1 reserved for unknown)
return (set)	- List of embeddings and associated labels
'''
def encode(tokens, label=None):
	encoder = KeyedVectors.load_word2vec_format('datasets/pubmed2018_w2v_200D.bin', binary=True) # Word2vec embeddings embeddings pre-trained on text from MEDLINE/PubMed Baseline 2018 by AUEB's NLP group http://nlp.cs.aueb.gr

	X = []
	y = []
	for token in tokens:
		if token in encoder.wv:
			X.append(encoder.wv[token])
			y.append(label)
		else:
			X.append(np.zeros(200))
			y.append(-1)

	return (X,y)

'''
Coverts sentence into tokens while filtering stop words (Glasgow) and punctuations
sentence (str)	- Paragraph or sentence of text to tokenize
return (list)	- List of tokens
'''
def tokenize(sentence):
	tokens = nltk.word_tokenize(sentence)
	tokens = [t1.lower() for t1 in tokens if t1 not in stop_words.ENGLISH_STOP_WORDS and t1 not in string.punctuation] # Remove punctuations & stop words using Glasgow stop words list
	return tokens

'''
Trains a Perceptron network to classify
cache (bool)	- Specify whether to save trained model as Pickle file
return (float)	- Trained model's accuracy score
'''
def train(cache = True):
	d1 = snomedct() + chv()
	d2 = sew()

	X1, y1 = encode(d1, 1) # Medical
	X2, y2 = encode(d2, 0) # Non-medical
	
	X = np.concatenate((X1, X2))
	y = np.concatenate((y1, y2))
	
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=10)

	nn = Perceptron(tol=1e-3, random_state=0)
	nn.fit(X_train, y_train)
	
	if cache: pickle.dump(nn, open(MODEL_NAME, 'wb'))

	return nn.score(X_test, y_test)

'''
Predicts labels for dataset based on trained model loaded as a Pickle file (needs model saved first via train())
sentence (str)	- Sentence to predict labels for
return (list)	- Pairs of token and label as a list
'''
def predict(sentence):
	nn = pickle.load(open(MODEL_NAME, 'rb'))
	
	tokens = tokenize(sentence)
	encodings = encode(tokens)[0]
	labels = nn.predict(encodings)

	results = []
	for i in range(0, len(tokens)):
		results.append((tokens[i], labels[i]))
	return results

""" Unit test for predict() """
def test():
	sentence = "n00bmaster69: Where can I find official documentation on difference between Salt Tablets and Table Salt. Several people online mention that Table Salt is just sodium and less of other minerals whereas Salt Tablets have sodium and more of other elements such as potassium. When I called a Pharmacist he said just the opposite. I have a cold or flu. He said Salt Tablets are just Sodium Chloride whereas Table Salt has sodium and other minerals. And when I asked why does Doctor prescribe Salt Tablets, the pharmacist said because it is harder to measure Table Salt, whereas Tablets are pre-portioned. Where to get official guidance on this?"

	for r in predict(sentence):
		print r
	
if __name__ == '__main__':
	test()