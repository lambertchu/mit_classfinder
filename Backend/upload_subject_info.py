import sys
import string
import ast
import psycopg2
from collections import defaultdict
from urllib2 import Request, urlopen

# connect to database
try:
    with open('pass.txt', 'r') as f:
    	for i, line in enumerate(f):
    		if i == 0:
    			password = line.rstrip('\n')
    		elif i == 1:
    			client_id = line.rstrip('\n')
    		elif i == 2:
    			client_secret = line.rstrip('\n')
    		elif i > 2:
    			break

	conn = psycopg2.connect("dbname='lambertchu' user='postgres' host='lambertchu.lids.mit.edu' password='%s'" % password)
except:
    print "Unable to connect to the database"
    sys.exit()
# conn.cursor will return a cursor object that you can use to perform queries
cursor = conn.cursor()


# Get list of all subjects
cursor.execute("SELECT DISTINCT Subject FROM complete_enrollment_data")

# Exclude classes from other schools
# HA is Harvard, W is Wellesley EXCEPT for WGS, MC is Mass College of Art
subjects = [s[0] for s in cursor.fetchall()]
print len(subjects)



count = 0

print "Beginning extraction of descriptions..."

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

	# 'description', 'title', 'prerequisites', 'instructors', 'subjectId', 'cluster', 'academicYear', 'units': '4-0-8 HASS-S', 'optional': None, 'termCode': '2015FA'}
	cursor.execute("INSERT INTO subject_info (SUBJECT) values (%s)", (sub_clean,))
	cursor.execute("UPDATE subject_info SET TITLE = (%s), PREREQS = (%s), UNITS = (%s), OPTIONAL = (%s), INSTRUCTORS = (%s), DESCRIPTION = (%s) WHERE SUBJECT = (%s)" , (info["title"], info["prerequisites"], info["units"], info["optional"], info["instructors"], info["description"], sub_clean))

	description = info["description"]
	if description != None:
		token_list = description.translate(None, string.punctuation).split()	# tokenize
		stop_list = set('for a of the and to in on as at from with but how about such eg ie'.split())	# remove common words
		keywords = [x for x in token_list if x not in stop_list]
		cursor.execute("UPDATE subject_info SET KEYWORDS = (%s) WHERE SUBJECT = (%s)", (keywords, sub_clean))


	# Insert time-relevance data
	cursor.execute("SELECT Term_Number FROM complete_enrollment_data WHERE Subject = %s", (subject,))
	terms = [t[0] for t in cursor.fetchall()]

	# Map term_number to its frequency
	d = defaultdict(int)
	for t in terms:
		d[t] += 1
	
	MAX_TERM_NUMBER = 16
	for i in xrange(1, MAX_TERM_NUMBER+1):
		cursor.execute("UPDATE subject_info SET TERM%s = (%s) WHERE SUBJECT = (%s)", (i, d[i], sub_clean))
	cursor.execute("UPDATE subject_info SET TOTAL = (%s) WHERE SUBJECT = (%s)", (len(terms), sub_clean))

	conn.commit()	# commit all changes

	count += 1
	if count >= 100:
		break
	