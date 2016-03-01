import sys
import string
import ast
from urllib2 import Request, urlopen
from gensim.models import Word2Vec
import db_wrapper

try:
    with open('pass.txt', 'r') as f:
    	for i, line in enumerate(f):
    		if i == 1:
    			client_id = line.rstrip('\n')
    		elif i == 2:
    			client_secret = line.rstrip('\n')
    		elif i > 2:
    			break

    print "Loading W2V model..."
    w2v_model = Word2Vec.load_word2vec_format('/Users/lambertchu/Documents/MIT/SuperUROP/NLP_Data/GoogleNews-vectors-negative300.bin', binary=True)

except:
	print "Error"
	sys.exit()


# Get list of all MIT subjects
subjects = db_wrapper.get_all_mit_classes()
count = 0

print "Beginning extraction of descriptions..."

# 'description', 'title', 'prerequisites', 'instructors', 'subjectId', 'cluster', 'academicYear', 'units': '4-0-8 HASS-S', 'optional': None, 'termCode': '2015FA'}
for subject in subjects:
	sub_clean = subject.strip()		# remove leading/trailing whitespace

	# PROBLEM: some classes use description from a different class (i.e. 22.00)
	term = "2015FA"
	url = "https://mit-public.cloudhub.io/coursecatalog/v2/terms/%s/subjects/%s" % (term, sub_clean)

	try:
		q = Request(url)
		q.add_header('client_id', client_id)
		q.add_header('client_secret', client_secret)
		result = urlopen(q).read()
	except:
		print "Error: " + sub_clean
		continue

	new_result = result.replace(" : null", " : None")		# format for conversion to Python dictionary
	dictionary = ast.literal_eval(new_result)				# conversion
	info = dictionary["item"]

	description = info["description"]
	if description != None:
		token_list = description.translate(None, string.punctuation).split()		# tokenize
		keywords = filter(lambda word: word in w2v_model.vocab, token_list)			# remove invalid words
	else:
		keywords = []

	try:
		db_wrapper.insert_subject_info(subject, sub_clean, info, description, keywords)
	except:
		print "Error inserting " + sub_clean
		continue

	count += 1
	if count % 500 == 0:
		print count
