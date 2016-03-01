import sys
import math
import csv
from scipy import spatial
import db_wrapper


"""
Generate recommendations for a given student using the "importance" methodology.
Recommendations are for EVERY term that the student was enrolled in.
"""
def generate_recommendations_by_importance(student, terms):
    # keys = terms, values = importance ratings for that term
    importance_ratings_by_term = {}

    for term in terms:
        student_classes = db_wrapper.get_student_classes_before_term(student, term)
        new_classes = [x for x in classes if x not in student_classes]

        # calculate "importance" of each class that hasn't been taken by the student
        importance_ratings = {}
        for cl in new_classes:
            total = 1
            for s in student_classes:
                total_number_class = totals[s]
                if total_number_class == 0:
                    break

                shared_number = int(shared_classes_table[class_table[cl]][class_table[s]])
                total *= math.exp(0.5 * shared_number / total_number_class)

                # TODO: include other modifiers here, i.e. term relevance and keyword match

            importance_ratings[cl] = total       # record total for this class

        importance_ratings_by_term[term] = sorted(importance_ratings, key=importance_ratings.get, reverse=True)
        # print importance_ratings_by_term[term][0:9]    # prints top 10 recommendations
    
    return importance_ratings_by_term
                

"""
Goal: generate recommendations using the "similarity" method (i.e. i2i CF)
"""
def generate_recommendations_similarity():

    # create hash table with keys = terms, values = dictionary mapping class to ranking
    # used for calculating errors
    # class_rankings_all_terms = {}

    terms = [4]
    student_classes = []

    for term in terms:
        #print term
        cursor.execute("SELECT DISTINCT Subject FROM complete_enrollment_data WHERE Identifier = %s AND Term_Number <= %s", (student,term))
        student_classes.append([c[0] for c in cursor.fetchall()])
        #print subjects

        # find "similarity" of each class - we exclude current subjects from similarity comparisons
        term_similarity_ratings = {}     # initialiaze similarity of each to 0
        for s in student_classes:
            for cl in classes:
                if cl not in student_classes:
                    pass
                    #term_similarity_ratings[cl] += # get rating from database


        #class_rankings_all_terms[term] = sorted(term_similarity_ratings, key=term_similarity_ratings.get, reverse=True)
        #print class_rankings_all_terms[term][0:7]    # prints top 8 recommendations



"""
Create hash table that maps each class to the total number of students enrolled in that class
"""
def create_totals_table(shared_classes_table):
    totals = {}
    count = 0
    for row in shared_classes_table:
        row_num = [int(x) for x in row]
        totals[classes[count]] = sum(row_num)
        count += 1
    return totals



"""
The following is executed on startup
"""
# Get list of all classes at MIT
classes = db_wrapper.get_all_classes()
num_classes = len(classes)

# Create hash table with keys = classes and values = index in list
class_table = {k:v for k, v in zip(classes, xrange(num_classes))}

# Recommend based upon student major
shared_classes_table = db_wrapper.get_matrix_by_major('6 3')
totals = create_totals_table(shared_classes_table)
