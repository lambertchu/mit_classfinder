"""
Overview:

randomly select X students as the test sample
for each of the remaining students
  reveal one more semester
      recommend the top classes for next semester
      calculate coverage & accuracy based upon S (selected next semester) and R (recommended)
"""

import sys
import math
import csv
import generate_recommendations
import db_wrapper


"""
Calculate error of recommendations for one student
Only applicable for recommendations of 2nd through last terms
"""
def calc_error(student, terms, class_rankings_by_term):
    term_errors = []

    for prev_term, cur_term in zip(terms, terms[1:]):
        subjects = db_wrapper.get_student_classes_of_term(student, cur_term)
        num_subjects = len(subjects)

        error = 0
        for subject in subjects:
            for i in xrange(0, len(class_rankings_by_term[prev_term])):
                if class_rankings_by_term[prev_term][i] == subject:
                    rank = i+1   # rank is not zero-indexed
                    break

            # error_factor = (rank of class - total classes taken) / size of the universe
            factor = max(0, (float(rank) - num_subjects) / (num_classes - num_subjects))
            error += factor

        # find the average error for that student's term
        error /= num_subjects
        term_errors.append(error)

    return term_errors



if __name__ == "__main__":
    # Get list of all classes at MIT
    classes = db_wrapper.get_all_classes()
    num_classes = len(classes)

    # Get 5000 random students as the test sample
    # ID range: 10001001 to 10027211 => 26211 students
    print "Randomly selecting 5000 students as test sample for cross validation..."
    target_students = db_wrapper.get_random_students(5000)  # TODO: make this a command line arg

    print "Calculating errors..."
    with open("cross_val_10B.csv", "wb") as f:
        writer = csv.writer(f)
        
        for student in target_students:
            writer.writerow([student])

            terms = db_wrapper.get_student_terms(student)
            writer.writerow(terms[1:])

            class_rankings_by_term = generate_recommendations.generate_recommendations_by_importance(student, terms)

            writer.writerow(calc_error(student, terms, class_rankings_by_term))
            writer.writerow([])
    sys.exit()