#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier

filePath = "data/training/training-data-complete.csv"
dataset = pd.read_csv(filePath)
# dataset = dataset.dropna()

X = dataset.iloc[:, 2:]
y = dataset.iloc[:, 1]
X = preprocessing.normalize(X)


#--------------------------------------------- Getting best params ---------------------------------------------------#

k_range = list(range(1, 31))
print(k_range)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)

classifier = KNeighborsClassifier(n_neighbors=3)
# classifier.fit(X_train, y_train)

param_grid = dict(n_neighbors=k_range)
print(param_grid)

grid = GridSearchCV(classifier, param_grid, cv=10, scoring='accuracy')

grid.fit(X,y)
# print(grid.best_estimator_)


#--------------------------------------------- Training use KNN ---------------------------------------------------#

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)

classifier = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
                     metric_params=None, n_jobs=None, n_neighbors=1, p=2,
                     weights='uniform')
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test) 
y_train_pred = classifier.predict(X_train)
# print(y_pred, y_test)

print("KNN Train Accuracy:", accuracy_score(y_train, y_train_pred)* 100, "%")
print("KNN Test Accuracy:", accuracy_score(y_test, y_pred) * 100, "%")
print(classification_report(y_test, y_pred))

# For k-fold cross validatation - can ignore for now 

# from sklearn.model_selection import KFold
# kf = KFold(n_splits=5)
# # for train_index, test_index in kf.split(X):
# #     print("Train:", train_index, "Test:", test_index)
    
# kfold = KFold(n_splits=5, random_state=100)
# classifier_kfold = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
#                      metric_params=None, n_jobs=None, n_neighbors=1, p=2,
#                      weights='uniform')
# results_kfold = cross_val_sc ore(classifier_kfold, X, y, cv=kfold)
# print("Accuracy: %.2f%%" % (results_kfold.mean()*100.0)) 

# print(X_test)


# In[7]:


from sklearn.externals import joblib
joblib.dump(classifier, "KNN.pkl")




