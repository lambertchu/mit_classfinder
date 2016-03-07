"""
Overview:

randomly select X students as the test sample
for each of the remaining students
  reveal one more semester
      recommend the top classes for next semester
      calculate coverage & accuracy based upon S (selected next semester) and R (recommended)
"""
import sys
import getopt
import math
import csv
import generate_recommendations
import db_wrapper



"""
Parse command line arguments
"""
# def parse_args(argv):
#     try:
#         opts, args = getopt.getopt(argv,"hi:o:",["numstudents=","ofile="])
#     except getopt.GetoptError:
#         print 'cross_validate.py -n <numstudents> -o <outputfile>'
#         sys.exit(2)
#     for opt, arg in opts:
#         if opt == '-h':
#             print 'cross_validate.py -n <numstudents> -o <outputfile>'
#             sys.exit()
#         elif opt in ("-n", "--numstudents"):
#             numstudents = arg
#         elif opt in ("-o", "--ofile"):
#             outputfile = arg
#     return (numstudents, outputfile)



"""
Calculate error of recommendations for one student
Only applicable for recommendations of 2nd through last terms
"""
def calc_error(student, terms, class_rankings_by_term):
    # TODO: error handling of classes not in rankings dictionary
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
            try:
                factor = max(0, (float(rank) - num_subjects) / (num_classes - num_subjects))
                error += factor
            except:
                print "Error: %s %s" % (student, subject)

        # find the average error for that student's term
        error /= num_subjects
        term_errors.append(error)

    return term_errors



if __name__ == "__main__":
    if (len(sys.argv) != 4):
        print "Invalid args"
        sys.exit(1)
    num_students = int(sys.argv[1])
    major = "15" #sys.argv[2]
    outputfile = sys.argv[3]

    # Get list of all classes at MIT
    classes = db_wrapper.get_all_mit_classes()
    num_classes = len(classes)
    print "Number of classes: %s" % num_classes

    # Get "num_students" random students as the test sample
    # ID range: 10001001 to 10027211 => 26211 students
    print "Randomly selecting %s students as test sample for cross validation..." % num_students
    random_students_and_terms = db_wrapper.get_random_students(num_students, major)



    ########## Create new matrix for the rest of the students in that major ###########
    matrix = [[0 for x in xrange(num_classes)] for y in xrange(num_classes)]

    # Get all student-classes pairs for terms in which the student was declared in that major
    student_class_dict = db_wrapper.get_student_classes_dict_by_major(major)

    # Remove students chosen randomly
    for student in random_students_and_terms:
        del student_class_dict[student]

    # Update the matrix
    for student, student_classes in student_class_dict.iteritems():
        index = 0
        while index < len(student_classes):
            sc1 = student_classes[index]
            sc1_pos = class_table[sc1]
            for sc2 in student_classes:
                matrix[sc1_pos][class_table[sc2]] += 1
            index += 1



    print "Calculating errors..."
    with open(outputfile, "wb") as f:
        writer = csv.writer(f)
        
        for student in random_students_and_terms:
            writer.writerow([student])

            terms = sorted(random_students_and_terms[student])
            writer.writerow(terms[1:])

            class_rankings_by_term = generate_recommendations.generate_recommendations_by_importance(student, terms)

            writer.writerow(calc_error(student, terms, class_rankings_by_term))
            writer.writerow([])
    sys.exit()