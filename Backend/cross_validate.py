"""
Overview:

randomly select X students as the test sample
for each of the remaining students
  reveal one more semester
      recommend the top classes for next semester
      calculate coverage & accuracy based upon S (selected next semester) and R (recommended)
"""
import sys
# import getopt
import math
import csv
from sets import Set
import db_wrapper
from generate_recs import generate_recommendations




"""
Calculate error of recommendations for one student (all terms).
Only applicable for recommendations of 2nd through last terms.
Returns a list of the errors of each term.
"""
def calc_error(student, terms, num_classes, class_rankings_by_term):
    # TODO: error handling of classes not in rankings dictionary
    term_errors = []

    for prev_term, cur_term in zip(terms, terms[1:]):
        taken_classes = db_wrapper.get_student_classes_of_term(student, cur_term)
        num_taken_classes = len(taken_classes)

        error = 0
        for subject in taken_classes:
            for i in xrange(0, len(class_rankings_by_term[prev_term])):
                rank = None
                if class_rankings_by_term[prev_term][i] == subject:
                    rank = i+1   # rank is not zero-indexed
                    break

            # error_factor = (rank of class - total classes taken) / size of the universe
            if rank == None:
                # TODO: set it equal to num_classes/2 ?
                rank = len(class_rankings_by_term[prev_term])

            factor = max(0, (float(rank) - num_taken_classes) / (num_classes - num_taken_classes))
            error += factor
            # print "Error: %s %s" % (student, subject)

        # find the average error for that student's term
        error /= num_taken_classes
        term_errors.append(error)

    return term_errors



if __name__ == "__main__":
    num_students = 500
    major = "15"
    outputfile = "Course_15_error_results.csv"


    # Get "num_students" random students as the test sample
    # ID range: 10001001 to 10027211 => 26211 students
    print "Randomly selecting %s students as test sample for cross validation..." % num_students
    random_students_and_terms = db_wrapper.get_random_students(num_students, major)
    assert len(random_students_and_terms) == num_students

    mit_classes = db_wrapper.get_all_mit_classes()
    num_classes = len(mit_classes)


    ########## Get data from database ###########
    # print "Creating matrix..."

    # # Create a dictionary mapping each student in the major to a list of classes that each one took.
    # student_class_dict = db_wrapper.get_student_classes_dict_by_major(major)
    # initial_dict_len = len(student_class_dict)
    

    # # Get all distinct classes taken by students (including randomly selected ones) in the given major
    # classes = Set([])
    # for student, student_classes in student_class_dict.iteritems():
    #     for cls in student_classes:
    #         classes.add(cls)

    # classes = list(classes)
    # num_classes = len(classes)
    # print "Number of distinct classes: %s" % num_classes




    ########## Create new matrix for the rest of the students in that major ###########

    # Create hash table to help with creating the shared_classes_table
    # class_table = {k:v for k, v in zip(classes, xrange(len(classes)))}

    # print classes
    # # Remove students chosen randomly
    # for student in random_students_and_terms:
    #     del student_class_dict[student]
    # assert len(student_class_dict) == initial_dict_len - num_students

    # Create the shared_classes_table matrix
    # shared_classes_table = create_shared_classes_table(num_classes, student_class_dict)
    # assert len(shared_classes_table) == num_classes
    # assert len(shared_classes_table[0]) == num_classes




    ########## Generate recommendations and calculate errors ###########

    print "Generating recommendations and calculating errors..."
    with open(outputfile, "wb") as f:
        writer = csv.writer(f)

        random_students = random_students_and_terms.keys()
        
        for student in random_students_and_terms:
            writer.writerow([student])

            terms = sorted(random_students_and_terms[student])
            writer.writerow(terms[1:])

            recommendations_by_term = generate_recommendations(student, major, random_students, terms)

            writer.writerow(calc_error(student, terms, num_classes, recommendations_by_term))
            writer.writerow([])
    sys.exit()