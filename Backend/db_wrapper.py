import sys
import random
import psycopg2

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


"""
Returns a list of all distinct classes taken by MIT undergraduates
"""
def get_all_classes():
	cursor.execute("SELECT DISTINCT Subject FROM complete_enrollment_data")
	classes = [cl[0] for cl in cursor.fetchall()]
	return classes


"""
Returns a list of all distinct majors at MIT
"""
def get_all_majors():
	cursor.execute("SELECT DISTINCT Major1 FROM complete_enrollment_data;")
	majors = [m[0] for m in cursor.fetchall()]
	return majors


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
Returns a list of all students that have taken the given class
"""
def get_students_of_class(cls):
	cursor.execute("SELECT DISTINCT Identifier FROM complete_enrollment_data WHERE Subject = %s", (cls,))
	students = [student[0] for student in cursor.fetchall()]
	return students


"""
Returns a list of randomly-selected student IDs
"""
def get_random_students(num):
	MIN_ID = 10001001
	MAX_ID = 10027211
	identifiers = [i for i in xrange(MIN_ID, MAX_ID+1)]
	random.shuffle(identifiers)
	return identifiers[0:num]


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
Get all student-classes pairs for terms in which the student was declared in that major
"""
def get_student_classes_dict_by_major(major):
	student_class_dict = {}
	cursor.execute("SELECT Identifier, Subject FROM complete_enrollment_data where Major1 = %s OR Major2 = %s", (major,major))
	pairs = [p for p in cursor.fetchall()]

	for identifier, cls in pairs:
		if identifier not in student_class_dict:
			student_class_dict[identifier] = [cls]
		else:
			student_class_dict[identifier].append(cls)

	return student_class_dict


conn = get_db_connection()
cursor = conn.cursor()