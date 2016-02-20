import sys
import csv
from scipy import spatial
import db_wrapper


# Get list of all classes at MIT
classes = db_wrapper.get_all_classes()
num_classes = len(classes)

# Create hash table with keys = classes and values = index in list
class_table = {k:v for k, v in zip(classes, xrange(num_classes))}

# Create nxn matrix with n = total number of classes
matrix = [[0 for x in xrange(num_classes)] for y in xrange(num_classes)]

# Create nxn similarity table
similarity_table = [[0 for x in xrange(num_classes)] for y in xrange(num_classes)]


# Implementation of item-to-item CF
print "Executing CF..."
for cls in classes:
    cls_pos = class_table[cls]
    students = db_wrapper.get_students_of_class(cls)

    for student in students:
        subjects = db_wrapper.get_student_classes_all(student)
        
        for subject in subjects:    # subjects are the classes that student has taken
            matrix[cls_pos][class_table[subject]] += 1     # goes down column, then across the row

    count = 0
    for c in classes:
        if count > cls_pos:
            break

        # compute similarity between cls and c
        cls_list = matrix[cls_pos]
        c_list = matrix[class_table[c]]
        similarity = 1 - spatial.distance.cosine(cls_list, c_list)  # CONSIDER PEARSON INSTEAD!
        similarity_table[cls_pos][class_table[c]] = similarity
        count += 1


# output matrix to CSV
with open("output_matrix.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(matrix)

# output data to CSV
with open("output_similarities.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerow(classes)
    writer.writerows(similarity_table)
sys.exit()