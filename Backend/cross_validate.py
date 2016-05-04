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



def calc_term_error(num_relevant_classes, taken_classes, recommendations):
    error = 0
    for subject in taken_classes:
        for i in xrange(0, len(recommendations)):
            rank = None
            if recommendations[i] == subject:
                rank = i+1   # rank is not zero-indexed
                break

        # error_factor = (rank of class - total classes taken) / size of the universe
        if rank != None:
            # factor = max(0, (float(rank) - len(relevant_classes)) / num_candidate_classes)
            factor = float(rank) / len(recommendations)
            error += factor
        # print "Error: %s %s" % (student, subject)

    # find the average error for that student's term
    error /= num_relevant_classes
    return error


"""
Calculate error of recommendations for one student (all terms).
Only applicable for recommendations of 2nd through last terms.
Returns a list of the errors of each term.
"""
def calc_error(student, terms, recommendations_by_term, candidate_classes_by_term):
    term_errors = []

    for prev_term, cur_term in zip(terms, terms[1:]):
        taken_classes = db_wrapper.get_student_classes_of_term(student, cur_term)

        num_candidate_classes = len(candidate_classes_by_term[prev_term])
        relevant_classes = [c for c in taken_classes if c in candidate_classes_by_term[prev_term]]

        if num_candidate_classes == 0:
            # print "%s satisfied all requirements on term %s" % (student, prev_term)
            term_errors.append(0)
            continue

        if len(relevant_classes) == 0:
            # print "No recommendations for %s in term %s" % (student, prev_term)
            term_errors.append(1)
            continue

        error = 0
        for subject in taken_classes:
            for i in xrange(0, len(recommendations_by_term[prev_term])):
                rank = None
                if recommendations_by_term[prev_term][i] == subject:
                    rank = i+1   # rank is not zero-indexed
                    break

            # error_factor = (rank of class - total classes taken) / size of the universe
            if rank != None:
                # factor = max(0, (float(rank) - len(relevant_classes)) / num_candidate_classes)
                factor = float(rank) / num_candidate_classes
                error += factor
            # print "Error: %s %s" % (student, subject)

        # find the average error for that student's term
        error /= len(relevant_classes)
        term_errors.append(error)

    return term_errors



if __name__ == "__main__":
    num_students = 100

    # 6-2, 6-3, 2, 18, 20, 8, 16 (16 1, 16 2), 15, 14, 7 (7 A)
    major = "18"
    outputfile = "Course_%s_error_results.csv" % major

    # mit_classes = db_wrapper.get_all_mit_classes()
    # course_18_classes = [c for c in mit_classes if c.startswith('18.')]
    # print course_18_classes


    # Get "num_students" random students as the test sample
    # ID range: 10001001 to 10027211 => 26211 students
    print "Randomly selecting %s students as test sample for cross validation..." % num_students
    random_students_and_terms = db_wrapper.get_random_students(num_students, major)
    random_students = random_students_and_terms.keys()
    assert len(random_students_and_terms) == num_students
    assert len(random_students) == num_students



    ########## Generate recommendations and calculate errors ###########

    print "Generating recommendations and calculating errors..."
    with open(outputfile, "wb") as f:
        writer = csv.writer(f)
        
        for student in random_students_and_terms:
            writer.writerow([student])

            terms = sorted(random_students_and_terms[student])
            recommendations_by_term, candidate_classes_by_term = generate_recommendations(student, major, random_students, terms)
            # recommendations_by_term, candidate_classes_by_term = generate_recommendations(student, major, random_students, terms, course_18_classes)


            writer.writerow(terms[1:])
            writer.writerow(calc_error(student, terms, recommendations_by_term, candidate_classes_by_term))
            writer.writerow([])
    sys.exit()