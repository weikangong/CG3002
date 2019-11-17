#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import GridSearchCV

filePath = "data/training/training-data-complete.csv"
dataset = pd.read_csv(filePath)
# dataset = dataset.dropna()

X = dataset.iloc[:, 2:]
y = dataset.iloc[:, 1]

# print(y)


# In[ ]:


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)

param_grid = {'C':[1,10,100,1000],'gamma':[1,0.1,0.001,0.0001], 'kernel':['linear','rbf']}
cv = StratifiedShuffleSplit(n_splits=5, test_size=0.3, random_state=42)
#grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv)
grid = GridSearchCV(SVC(),param_grid,refit = True, verbose=0)
grid.fit(X_train, y_train)

print("The best parameters are %s with a score of %0.2f" % (grid.best_params_, grid.best_score_))


# In[ ]:


SVM1 = SVC(C=100, gamma=0.0001, kernel='rbf')
SVM1.fit(X_train,y_train)
y_pred = SVM1.predict(X_test)
SVM1_train_acc = (SVM1.score(X_train, y_train)) * 100
SVM1_test_acc = (SVM1.score(X_test, y_test)) * 100
print("SVM Train Accuracy:", SVM1_train_acc, "%")
print("SVM Test Accuracy:", SVM1_test_acc, "%")


# In[ ]:




