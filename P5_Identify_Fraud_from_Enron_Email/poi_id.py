#!/usr/bin/python
# -*- coding: utf-8 -*-    
import sys 
import pickle 
import matplotlib 
from matplotlib import pyplot 
sys.path.append("../tools/") 

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
from numpy import mean 
from sklearn.feature_selection import SelectKBest 
from sklearn.feature_selection import SelectPercentile, f_classif 
from sklearn.preprocessing import MinMaxScaler 
from sklearn.cross_validation import train_test_split 
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn import tree
from sklearn.grid_search import GridSearchCV

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi'] # You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
person_num = len(data_dict)
feature_num = len(data_dict[data_dict.keys()[0]]) - 1
data_num = person_num * feature_num

poi_num = 0
for dic in data_dict.values():
    if dic['poi'] == 1:
        poi_num += 1

non_poi_num = 0
for dic in data_dict.values():
    if dic['poi'] == 0:
        non_poi_num += 1
print "Number of persons:", person_num
print "Number of data points:", data_num
print "Number of features:", feature_num
print "Number of POIs:", poi_num
print "Number of non-POIs:", non_poi_num

# for dic in data_dict.values():
#   matplotlib.pyplot.scatter(dic['salary'], dic['bonus'])

# matplotlib.pyplot.xlabel("salary")
# matplotlib.pyplot.ylabel("bonus")
# matplotlib.pyplot.show()

# find a outlier: TOTAL
for k,v in data_dict.items():
    if v['salary'] != 'NaN' and v['salary'] > 10000000:
        print k

# delate TOTAL
del data_dict['TOTAL']
del data_dict['THE TRAVEL AGENCY IN THE PARK']
del data_dict['LOCKHART EUGENE E']


### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.
my_dataset = data_dict

# costom aggregate features
# Communication:
for item in my_dataset:
    person = my_dataset[item]
    if (all([person['from_poi_to_this_person'] != 'NaN',
             person['from_this_person_to_poi'] != 'NaN',
             person['to_messages'] != 'NaN',
             person['from_messages'] != 'NaN'])):
        fraction_from_poi = float(person['from_poi_to_this_person']) / float(person['to_messages'])
        person['fraction_from_poi'] = fraction_from_poi
        fraction_to_poi = float(person['from_this_person_to_poi']) / float(person['from_messages'])
        person['fraction_to_poi'] = fraction_to_poi
    else:
        person['fraction_from_poi'] = person['fraction_to_poi'] = 0

# Financial:
for item in my_dataset:
    person = my_dataset[item]
    if (all([person['salary'] != 'NaN', 
             person['total_stock_value'] != 'NaN', 
             person['exercised_stock_options'] != 'NaN',
             person['bonus'] != 'NaN'
            ])):
        person['wealth'] = sum([person[field] for field in ['salary',
                                                        'total_stock_value',
                                                        'exercised_stock_options',
                                                        'bonus']])
    else:
        person['wealth'] = 'NaN'

my_features = features_list + ['fraction_from_poi',
                               'fraction_to_poi',
                               'shared_receipt_with_poi',
                               'expenses',
                               'loan_advances',
                               'long_term_incentive',
                               'other',
                               'restricted_stock',
                               'restricted_stock_deferred',
                               'deferral_payments',
                               'deferred_income',
                               'salary',
                               'total_stock_value',
                               'exercised_stock_options',
                               'total_payments',
                               'bonus',
                               'wealth']

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, my_features, sort_keys = True)
labels, features = targetFeatureSplit(data)

print "Intuitive features:", my_features

# Scale features
scaler = MinMaxScaler()
features = scaler.fit_transform(features)

# K-best features
k_best = SelectKBest(k = 5)
k_best.fit(features, labels)

results_list = zip(k_best.get_support(), my_features[1:], k_best.scores_)
results_list = sorted(results_list, key = lambda x: x[2], reverse = True)
print "K-best features:", results_list

## 5 best features chosen by SelectKBest
my_features = features_list + ['exercised_stock_options',
                               'total_stock_value',
                               'bonus',
                               'salary',
                               'fraction_to_poi'
                               ]

data = featureFormat(my_dataset, my_features, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

def test_clf(grid_search, features, labels, parameters, iterations = 100):

    precision, recall = [], []
    for iteration in range(iterations):
        features_train, features_test, labels_train, labels_test = train_test_split(features, labels, random_state = iteration)
        grid_search.fit(features_train, labels_train)
        predictions = grid_search.predict(features_test)
        precision = precision + [precision_score(labels_test, predictions)]
        recall = recall + [recall_score(labels_test, predictions)]
        if iteration % 10 == 0:
            sys.stdout.write('.')
    print '\nPrecision:', mean(precision)
    print 'Recall:', mean(recall)
    best_params = grid_search.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        print '%s=%r,' % (param_name, best_params[param_name])

# def test_clf(grid_search, features, labels, parameters):
#     precision = 0.0
#     recall = 0.0
#     features_train, features_test, labels_train, labels_test = train_test_split(features, labels, random_state = 100)
#     grid_search.fit(features_train, labels_train)
#     predictions = grid_search.predict(features_test)
#     precision = precision_score(labels_test, predictions)
#     recall = recall_score(labels_test, predictions)
#     print '\nPrecision:', precision
#     print 'Recall:', recall
#     print '=========='
#     best_params = grid_search.best_estimator_.get_params()
#     for param_name in sorted(parameters.keys()):
#         print '%s=%r,' % (param_name, best_params[param_name])


# Provided to give you a starting point. Try a variety of classifiers.
# GaussianNB
from sklearn.naive_bayes import GaussianNB
clf = GaussianNB()
parameters = {}
grid_search = GridSearchCV(clf, parameters)
print '\n==========\nGaussianNB:'
test_clf(grid_search, features, labels, parameters)

# DecisionTree
clf = tree.DecisionTreeClassifier()
parameters = {'criterion': ['gini', 'entropy'],
              'min_samples_split': [2, 10, 20],
              'max_depth': [None, 2, 5, 10],
              'min_samples_leaf': [1, 5, 10],
              'max_leaf_nodes': [None, 5, 10, 20]}
grid_search = GridSearchCV(clf, parameters)
print '\n==========\nDecisionTree:'
test_clf(grid_search, features, labels, parameters)

# RandomForestClassifier
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier()
parameters = {}
grid_search = GridSearchCV(clf, parameters)
print '\n==========\nRandomForestClassifier:'
test_clf(grid_search, features, labels, parameters)

# AdaBoost
from sklearn.ensemble import AdaBoostClassifier
clf = AdaBoostClassifier()
parameters = {'n_estimators': [2, 5, 10, 20, 30, 40, 50],
              'algorithm': ['SAMME', 'SAMME.R'],
              'learning_rate': [.5,.8, 1, 1.2, 1.5]}
grid_search = GridSearchCV(clf, parameters)
print '\n==========\nAdaBoost:'
test_clf(grid_search, features, labels, parameters)


# Results:
# GaussianNB:
# Precision: 0.423174603175
# Recall: 0.309916666667

# DecisionTree:
# Precision: 0.202801587302
# Recall: 0.220619047619
# criterion='entropy',
# max_depth=None,
# max_leaf_nodes=None,
# min_samples_leaf=10,
# min_samples_split=2

# RandomForestClassifier:
# Precision: 0.32819047619
# Recall: 0.173404761905

# AdaBoost:
# Precision: 0.398380952381
# Recall: 0.244841269841
# algorithm='SAMME',
# learning_rate=0.5,
# n_estimators=10

# So GaussianNB is better.

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html
features_list = my_features
# Example starting point. Try investigating other evaluation techniques!
from sklearn.cross_validation import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)

from sklearn.naive_bayes import GaussianNB
clf = GaussianNB()
### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, my_features)