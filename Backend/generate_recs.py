import math
from sets import Set
import db_wrapper, get_new_classes


"""
Create a matrix that records the number of students that took each pair of classes
"""
def create_shared_classes_table(major, random_students, all_classes, class_table):
    num_classes = len(all_classes)
    pairs = db_wrapper.get_student_classes_pairs(major)


    # Create dictionary mapping each student to a list of classes taken
    student_class_dict = {}
    for identifier, cls in pairs:
        if identifier in random_students:
            continue

        if identifier not in student_class_dict and cls in all_classes:
            student_class_dict[identifier] = [cls]
        elif cls in all_classes:
            student_class_dict[identifier].append(cls)

    matrix = [[0 for x in xrange(num_classes)] for y in xrange(num_classes)]
    for student, classes in student_class_dict.iteritems():
        for sc1 in classes:
            for sc2 in classes:
                matrix[class_table[sc1]][class_table[sc2]] += 1

    return matrix



"""
Calculate the "importance" rating of one new class
"""
def calculate_rating(new_class, student_classes, class_table, shared_classes_table):
    rating = 1
    for s in student_classes:
        index = class_table[s]
        total_number_class = shared_classes_table[index][index]
        if total_number_class == 0:
            break

        try:
            shared_number = int(shared_classes_table[class_table[new_class]][index])
            rating *= math.exp(0.5 * shared_number / total_number_class)
        except:
            print (new_class, s)

    return rating



"""
Returns a list of recommendations for a given student in a single term/semester.
"""
def generate_recommendations(student, major, term, random_students):
# def generate_recommendations(student, major, term, random_students, specific_classes):
    student_classes = db_wrapper.get_student_classes_before_term(student, term)
    new_classes = get_new_classes.get_classes_to_take(major, student_classes)
    # new_classes = [c for c in specific_classes if c not in student_classes]
    all_classes = student_classes + new_classes

    
    class_table = {k:v for k, v in zip(all_classes, xrange(len(all_classes)))}
    shared_classes_table = create_shared_classes_table(major, random_students, all_classes, class_table)     # consider caching


    # Calculate "importance" of each class that hasn't been taken by the student
    importance_ratings = {}

    for new_class in new_classes:
        rating = calculate_rating(new_class, student_classes, class_table, shared_classes_table)
        importance_ratings[new_class] = rating

    # Create list of classes in order of popularity
    recommendations = sorted(importance_ratings, key=importance_ratings.get, reverse=True)

    return recommendations
