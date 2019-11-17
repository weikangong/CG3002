#!/usr/bin/env python
# coding: utf-8

# In[4]:


from sklearn import preprocessing
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
import pandas as pd


# In[5]:


filePath = "training-data-complete-8nov-trimmed.csv"
dataset = pd.read_csv(filePath)
X = dataset.iloc[:, 2:]
y = dataset.iloc[:, 1]
X = preprocessing.normalize(X)


# In[6]:


print(X.shape)


# In[7]:


X_new = SelectKBest(chi2, k=30).fit_transform(X, y)
print(X_new.shape)


# In[ ]:




