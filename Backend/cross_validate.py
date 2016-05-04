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
Returns the error of recommendations for one term of a single student.
"""
def calc_error(student, term, recommendations):
    taken_classes = db_wrapper.get_student_classes_of_term(student, term)
    relevant_classes = [c for c in taken_classes if c in recommendations]

    # print "Recommendations: %s" % recommendations
    # print "Relevant: %s" % relevant_classes

    if len(recommendations) == 0 or len(relevant_classes) == 0:
        return None

    error = 0
    for subject in relevant_classes:
        rank = None
        for i in xrange(0, len(recommendations)):
            if subject == recommendations[i]:
                rank = i
                break

        # error_factor = (rank of class - total classes taken) / size of the universe
        if rank != None:
            factor = float(rank) / len(recommendations)
            error += factor

    # find the average error for that student's term
    error /= len(relevant_classes)
    return error



if __name__ == "__main__":
    num_students = 100

    # 6-2, 6-3, 2, 18, 20, 8, 16 (16 1, 16 2), 15, 14, 7 (7 A)
    major = "6 3"
    outputfile = "Course_%s_error_results.csv" % major

    # mit_classes = db_wrapper.get_all_mit_classes()
    # specific_classes = [c for c in mit_classes if c.startswith('18.')]
    # print specific_classes


    # Get "num_students" random students as the test sample
    # ID range: 10001001 to 10027211 => 26211 students
    print "Randomly selecting %s students as test sample for cross validation..." % num_students
    random_students_and_terms = db_wrapper.get_random_students(num_students, major)
    random_students = random_students_and_terms.keys()
    assert len(random_students_and_terms) == num_students
    assert len(random_students) == num_students



    ########## Generate recommendations and calculate errors ###########
    total_errors = {}
    for i in xrange(1, 17):
        total_errors[i] = 0.0

    total_students = {}
    for i in xrange(1, 17):
        total_students[i] = 0


    print "Generating recommendations and calculating errors..."
    with open(outputfile, "wb") as f:
        writer = csv.writer(f)
        
        for student in random_students_and_terms:
            writer.writerow([student])

            terms = sorted(random_students_and_terms[student])

            student_terms = []
            student_term_errors = []
            for term in terms:
                recommendations = generate_recommendations(student, major, term, random_students)
                # recommendations = generate_recommendations(student, major, term, random_students, specific_classes)

                term_error = calc_error(student, term, recommendations)
                
                if term_error != None:
                    student_terms.append(term)
                    student_term_errors.append(term_error)
                    total_errors[term] += term_error
                    total_students[term] += 1

            assert len(student_terms) == len(student_term_errors)
            writer.writerow(student_terms)
            writer.writerow(student_term_errors)
            writer.writerow([])


        term_nums = ["Term Number"]
        total_errors_list = ["Total Error"]
        total_students_list = ["Number of Students"]
        term_averages_list = ["Average Error"]
        for term in xrange(1, 17):
            term_nums.append(term)
            if total_students[term] == 0:
                assert total_errors[term] == 0
                term_averages_list.append(None)
            else:
                term_averages_list.append(total_errors[term] / total_students[term])

            total_errors_list.append(total_errors[term])
            total_students_list.append(total_students[term])


        writer.writerow(["Stats"])
        writer.writerow(term_nums)
        writer.writerow(total_errors_list)
        writer.writerow(total_students_list)
        writer.writerow(term_averages_list)

    sys.exit()