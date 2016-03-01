import sys
import csv
import db_wrapper


# Get list of all classes at MIT
classes = db_wrapper.get_all_classes()
num_classes = len(classes)
print num_classes


# Create hash table with keys = classes and values = index in list
class_table = {k:v for k, v in zip(classes, xrange(num_classes))}


# Get distinct majors
majors = db_wrapper.get_all_majors()
print len(majors)


#done_majors = db_wrapper.get_majors_in_shared_classes_by_major()

# Create nxn matrices (to be stored in database)
for major in majors:
    print major.strip()
    if major.strip() != "15":
        continue

    print "Creating matrix of shared classes for " + major
    matrix = [[0 for x in xrange(num_classes)] for y in xrange(num_classes)]

    # Get all student-classes pairs for terms in which the student was declared in that major
    student_class_dict = db_wrapper.get_student_classes_dict_by_major(major)

    # Update the matrix
    for student, student_classes in student_class_dict.iteritems():
        index = 0
        while index < len(student_classes):
            sc1 = student_classes[index]
            sc1_pos = class_table[sc1]
            for sc2 in student_classes:
                matrix[sc1_pos][class_table[sc2]] += 1
            index += 1


    # Output matrix to CSV
    # print "Outputting..."
    # with open("test_classes_popularity.csv", "wb") as f:
    #     writer = csv.writer(f)
    #     writer.writerows(matrix)

    print "Inserting matrix to database..."
    major_cleaned = major.strip()
    db_wrapper.insert_matrix_by_major(major_cleaned, matrix)
