#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPClassifier


# In[2]:


filePath = "data/training/training-data-complete-14nov-trimmed2.csv"
dataset = pd.read_csv(filePath)
# dataset = dataset.dropna()

X = dataset.iloc[:, 2:]
y = dataset.iloc[:, 1]
X = preprocessing.normalize(X)
# print(y)


# In[ ]:


#--------------------------------------------- Getting best params ---------------------------------------------------#

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)
#
# mlp = MLPClassifier(max_iter=100)
# tuned_parameters = {
#     'hidden_layer_sizes': [(50,50,50), (50,100,50), (100,50,50), (50,50,100), (50,100,100), (100,100,50), (100,50,100), (100,)],
#     'activation': ['logistic', 'tanh', 'relu'],
#     'solver': ['lbfgs', 'sgd', 'adam'],
#     'alpha': [0.0001, 0.05],
#     'learning_rate': ['constant','adaptive'],
# }
#
# grid_search = GridSearchCV(mlp, tuned_parameters, n_jobs=-1, cv=5)
#
# grid_search.fit(X_train, y_train)
#
# print(grid_search.best_params_)
#
#
# # In[4]:


#----------------------------------------- Training use Neural Net ---------------------------------------------------#

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)

classifier = MLPClassifier(hidden_layer_sizes=(100,50,100), activation='tanh', 
                          solver='adam', alpha=0.0001, learning_rate='adaptive')

classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test) 
y_train_pred = classifier.predict(X_train)

print("NN Train Accuracy:", accuracy_score(y_train, y_train_pred)* 100, "%")
print("NN Test Accuracy:", accuracy_score(y_test, y_pred) * 100, "%")
print(classification_report(y_test, y_pred))


# In[ ]:


# In[8]:


from sklearn.externals import joblib
joblib.dump(classifier, "NN3.pkl", protocol=2)


# In[ ]:


