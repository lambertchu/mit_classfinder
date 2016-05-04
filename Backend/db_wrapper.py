import sys
import psycopg2
from collections import defaultdict

"""
Returns a connection to the database
"""
def get_db_connection():
	try:
	    with open('pass.txt', 'r') as f:
	        for i, line in enumerate(f):
	            if i == 0:
	                password = line.rstrip('\n')
	            else:
	                break
	                
	    conn = psycopg2.connect("dbname='lambertchu' user='postgres' host='lambertchu.lids.mit.edu' password='%s'" % password)
	except:
	    print "Unable to connect to the database"
	    sys.exit()
	# conn.cursor will return a cursor object that you can use to perform queries
	return conn





################## GENERAL ##################

"""
Returns a list of all distinct classes taken by MIT undergraduates
"""
def get_all_classes():
	cursor.execute("SELECT DISTINCT Subject FROM complete_enrollment_data")
	classes = [cl[0] for cl in cursor.fetchall()]
	return classes


"""
Returns a list of all distinct MIT classes taken by MIT undergraduates
"""
def get_all_mit_classes():
	classes = get_all_classes()
	mit_classes = []

	for cl in classes:
		if cl == None or cl[0:2] == "HA" or cl[0:2] == "MC" or (cl[0:1] == "W" and cl[0:3] != "WGS"):
			continue
		mit_classes.append(cl)

	return mit_classes

"""
Returns a list of all distinct majors at MIT
"""
def get_all_majors():
	cursor.execute("SELECT DISTINCT Major1 FROM complete_enrollment_data;")
	majors = [m[0] for m in cursor.fetchall()]
	return majors





################## STUDENT-BASED ##################

"""
Returns the list of terms that the given student has enrolled in
"""
def get_student_terms(student):
    cursor.execute("SELECT DISTINCT Term_Number FROM complete_enrollment_data WHERE Identifier = %s", (student,))
    terms = sorted([term[0] for term in cursor.fetchall()])
    return terms


"""
Returns a list of all classes taken by a given student
"""
def get_student_classes_all(student):
	cursor.execute("SELECT DISTINCT Subject FROM complete_enrollment_data WHERE Identifier = %s", (student,))
	subjects = [subject[0] for subject in cursor.fetchall()]
	return subjects


"""
Returns a list of classes that the student has taken during the given term
"""
def get_student_classes_of_term(student, term):
	cursor.execute("SELECT DISTINCT Subject FROM complete_enrollment_data WHERE Identifier = %s AND Term_Number = %s", (student, term))
	subjects = [subject[0] for subject in cursor.fetchall()]
	return subjects


"""
Returns a list of classes that the student has taken prior to the given term
"""
def get_student_classes_before_term(student, term):
	cursor.execute("SELECT DISTINCT Subject FROM complete_enrollment_data WHERE Identifier = %s AND Term_Number < %s", (student, term))
	subjects = [subject[0] for subject in cursor.fetchall()]
	return subjects


"""
Returns a list of all students that have taken the given class
"""
def get_students_of_class(cls):
	cursor.execute("SELECT DISTINCT Identifier FROM complete_enrollment_data WHERE Subject = %s", (cls,))
	students = [student[0] for student in cursor.fetchall()]
	return students


"""
Returns a dictionary of randomly-selected students that are of the given major, mapped to terms that they declared the major
"""
def get_random_students(num, major):
	import random
	student_class_dict = get_student_terms_dict_by_major(major)
	students = student_class_dict.keys()
	random.shuffle(students)

	random_keys = students[0:num]
	subset = {x: student_class_dict[x] for x in random_keys}

	return subset





################## MAJOR-BASED ##################

"""
Returns a 2D list of "class enrollment" for the given major
"""
def get_matrix_by_major(major):
	cursor.execute("SELECT Matrix FROM shared_classes_by_major WHERE Major = %s", (major,))
	shared_classes_table = cursor.fetchone()[0]
	return shared_classes_table


"""
Inserts (into the db) a 2D list of "class enrollment" for the given major.
See http://initd.org/psycopg/docs/usage.html
"""
def insert_matrix_by_major(major, matrix):
	cursor.execute("INSERT INTO shared_classes_by_major (MAJOR, MATRIX) VALUES (%s, %s)", (major, matrix))
	conn.commit()



"""
"""
def get_student_classes_pairs(major):
	cursor.execute("SELECT Identifier, Subject FROM complete_enrollment_data where Major1 = %s OR Major2 = %s", (major,major))
	pairs = [p for p in cursor.fetchall()]
	return pairs


"""
Get all student-classes pairs for terms in which students were declared in that major.
Returns a dictionary mapping each student to a list of classes taken.
"""
def get_student_classes_dict_by_major(major):
	student_class_dict = {}
	pairs = get_student_classes_pairs(major)

	for identifier, cls in pairs:
		if identifier not in student_class_dict:
			student_class_dict[identifier] = [cls]
		else:
			student_class_dict[identifier].append(cls)

	return student_class_dict


"""
Map student to terms in which he/she declared the given major
"""
def get_student_terms_dict_by_major(major):
	student_class_dict = {}
	cursor.execute("SELECT Identifier, Term_Number FROM complete_enrollment_data where Major1 = %s OR Major2 = %s", (major,major))
	data = [d for d in cursor.fetchall()]

	for identifier, term in data:
		if identifier not in student_class_dict:
			student_class_dict[identifier] = [term]
		else:
			if term not in student_class_dict[identifier]:
				student_class_dict[identifier].append(term)

	return student_class_dict



"""
Get the frequency of classes taken by students of the given major in the given term
"""
def get_class_frequency_by_major_and_term(major, term):
	cursor.execute("SELECT Subject FROM complete_enrollment_data where Term_Number = %s AND (Major1 = %s OR Major2 = %s)", (term,major,major))
	subjects = [s[0] for s in cursor.fetchall()]
	subjects_dict = {}

	for subject in subjects:
		if subject not in subjects_dict:
			subjects_dict[subject] = 1
		else:
			subjects_dict[subject] += 1

	return subjects_dict


"""
Get most popular classes in the given major for the given semester. Uses get_class_frequency_by_major_and_term() as a helper
"""
def get_most_popular_classes(major, term):
	subjects_dict = get_class_frequency_by_major_and_term(major, term)
	sorted_subjects = sorted(subjects_dict, key=subjects_dict.get, reverse=True)

	classes = []
	for subject in sorted_subjects[0:20]:
		cursor.execute("SELECT Title FROM subject_info WHERE Subject = %s", (subject,))
		title = cursor.fetchone()
		info = (subject, title, subjects_dict[subject])
		classes.append(info)

	return classes


"""
Get all majors at MIT
"""
def get_majors_in_shared_classes_by_major():
	cursor.execute("SELECT Major FROM shared_classes_by_major")
	majors = [major[0] for major in cursor.fetchall()]
	return majors





################## CLASS-BASED ##################

"""
Parse subject info and insert to database
"""
def insert_subject_info(subject, sub_clean, info, description, keywords):
	# Get term-relevance data
	cursor.execute("SELECT Term_Number FROM complete_enrollment_data WHERE Subject = %s", (subject,))
	terms = [t[0] for t in cursor.fetchall()]

	# Map term_number to its frequency
	d = defaultdict(int)
	for t in terms:
		d[t] += 1
	
	term1, term2, term3, term4, term5, term6, term7, term8, term9, term10, term11, term12, term13, term14, term15, term16 = d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9], d[10], d[11], d[12], d[13], d[14], d[15], d[16]
	total = len(terms)

	cursor.execute("INSERT INTO subject_info (SUBJECT, TITLE, PREREQS, UNITS, OPTIONAL, INSTRUCTORS, DESCRIPTION, KEYWORDS, TERM1, TERM2, TERM3, TERM4, TERM5, TERM6, TERM7, TERM8, TERM9, TERM10, TERM11, TERM12, TERM13, TERM14, TERM15, TERM16, TOTAL) values %s", [(sub_clean, info["title"], info["prerequisites"], info["units"], info["optional"], info["instructors"], description, keywords, term1, term2, term3, term4, term5, term6, term7, term8, term9, term10, term11, term12, term13, term14, term15, term16, total)])
	conn.commit()


conn = get_db_connection()
cursor = conn.cursor()