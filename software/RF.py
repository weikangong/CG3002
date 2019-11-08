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
from sklearn.ensemble import RandomForestClassifier


# In[3]:


# filePath = "./training-data-complete-23+25oct-trimmed.csv"
filePath = "./training-data-complete-8nov-trimmed.csv"
dataset = pd.read_csv(filePath)
# dataset = dataset.dropna()

X = dataset.iloc[:, 2:]
y = dataset.iloc[:, 1]
X = preprocessing.normalize(X)
# print(y)


# In[ ]:


#--------------------------------------------- Getting best params ---------------------------------------------------#
#
# k_range = list(range(1, 31))
# print(k_range)
#
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)
#
# classifier = RandomForestClassifier()
# # classifier.fit(X_train, y_train)
#
# param_grid = {
#     'n_estimators': [200, 500],
#     'max_features': ['auto', 'sqrt', 'log2'],
#     'max_depth' : [4,5,6,7,8],
#     'criterion' :['gini', 'entropy']
# }
# print(param_grid)
#
# grid = GridSearchCV(estimator=classifier, param_grid=param_grid, cv= 5)
#
# grid.fit(X,y)
# print(grid.best_estimator_)


# In[4]:


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)

rf = RandomForestClassifier(bootstrap=True, class_weight=None, criterion='entropy',
                       max_depth=7, max_features='log2', max_leaf_nodes=None,
                       min_impurity_decrease=0.0, min_impurity_split=None,
                       min_samples_leaf=1, min_samples_split=2,
                       min_weight_fraction_leaf=0.0, n_estimators=200,
                       n_jobs=None, oob_score=False, random_state=None,
                       verbose=0, warm_start=False)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
y_train_pred = rf.predict(X_train)

print("Random Forest Train Accuracy:", accuracy_score(y_train, y_train_pred)* 100, "%")
print("Random Forest Test Accuracy:", accuracy_score(y_test, y_pred) * 100, "%")
print(classification_report(y_test, y_pred))


# In[8]:


from sklearn.externals import joblib
joblib.dump(rf, "RF5.pkl", protocol=2)


# In[ ]:
