#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
from glob import glob 
from scipy.fftpack import fft


# In[2]:


files = glob('./data/individual_8nov/*.csv')

full_df = pd.DataFrame()

for filePath in files:
#     print(filePath)
    
    colNames=['index', 'x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'x3', 'y3', 'z3', 
          'x4', 'y4', 'z4', 'x5', 'y5', 'z5', 'nan', 'class', 'null', 'index.1'] 
#     dataset = pd.read_csv(filePath, names=colNames, header=None)
    dataset = pd.read_csv(filePath)
#     print(len(dataset.columns))
    if (len(dataset.columns)==13):
        colNames=['x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'x3', 'y3', 'z3', 
          'x4', 'y4', 'z4', 'class'] 
        dataset.columns = colNames
    else:
#         print(dataset)
        colNames=['index', 'x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'x3', 'y3', 'z3', 
          'x4', 'y4', 'z4', 'x5', 'y5', 'z5', 'nan', 'class', ] 
        dataset.columns = colNames
        dataset = dataset.drop(columns=['x5', 'y5', 'z5', 'nan', 'index'])
        
    dataset = dataset.iloc[150:-150]
#     print(dataset)
    dataset2 = dataset.iloc[15:]
    df = dataset.groupby('class')
    df2 = dataset2.groupby('class')

    N=30

    df_mean1 = dataset.groupby([np.arange(len(dataset.index))//N, 'class'], axis=0).mean()
    df_mean1.rename(columns={'x1':'x1_mean', 'y1':'y1_mean', 'z1':'z1_mean', 'x2':'x2_mean', 'y2':'y2_mean', 'z2':'z2_mean',
                            'x3':'x3_mean', 'y3':'y3_mean', 'z3':'z3_mean', 'x4':'x4_mean', 'y4':'y4_mean', 'z4':'z4_mean'}, inplace=True)

    df_mean2 = dataset2.groupby([np.arange(len(dataset2.index))//N,'class'], axis=0).mean()
    df_mean2.rename(columns={'x1':'x1_mean', 'y1':'y1_mean', 'z1':'z1_mean', 'x2':'x2_mean', 'y2':'y2_mean', 'z2':'z2_mean',
                            'x3':'x3_mean', 'y3':'y3_mean', 'z3':'z3_mean', 'x4':'x4_mean', 'y4':'y4_mean', 'z4':'z4_mean'}, inplace=True)

    df_max1 = dataset.groupby([np.arange(len(dataset.index))//N,'class'], axis=0).max()
    df_max1.rename(columns={'x1':'x1_max', 'y1':'y1_max', 'z1':'z1_max', 'x2':'x2_max', 'y2':'y2_max', 'z2':'z2_max',
                           'x3':'x3_max', 'y3':'y3_max', 'z3':'z3_max', 'x4':'x4_max', 'y4':'y4_max', 'z4':'z4_max'}, inplace=True)
    df_max2 = dataset2.groupby([np.arange(len(dataset2.index))//N,'class'], axis=0).max()
    df_max2.rename(columns={'x1':'x1_max', 'y1':'y1_max', 'z1':'z1_max', 'x2':'x2_max', 'y2':'y2_max', 'z2':'z2_max',
                           'x3':'x3_max', 'y3':'y3_max', 'z3':'z3_max', 'x4':'x4_max', 'y4':'y4_max', 'z4':'z4_max'}, inplace=True)

    df_var1 = dataset.groupby([np.arange(len(dataset.index))//N,'class'], axis=0).var()
    df_var1.rename(columns={'x1':'x1_var', 'y1':'y1_var', 'z1':'z1_var', 'x2':'x2_var', 'y2':'y2_var', 'z2':'z2_var',
                           'x3':'x3_var', 'y3':'y3_var', 'z3':'z3_var', 'x4':'x4_var', 'y4':'y4_var', 'z4':'z4_var'}, inplace=True)
    df_var2 = dataset2.groupby([np.arange(len(dataset2.index))//N,'class'], axis=0).var()
    df_var2.rename(columns={'x1':'x1_var', 'y1':'y1_var', 'z1':'z1_var', 'x2':'x2_var', 'y2':'y2_var', 'z2':'z2_var',
                           'x3':'x3_var', 'y3':'y3_var', 'z3':'z3_var', 'x4':'x4_var', 'y4':'y4_var', 'z4':'z4_var'}, inplace=True)

    df1 = df_mean1.join(df_max1)
    df1 = df1.join(df_var1)

    df2 = df_mean2.join(df_max2)
    df2 = df2.join(df_var2)
    combine_df = pd.DataFrame()
    combine_df = df1.append(df2)
    combine_df = combine_df.dropna()
#     print(combine_df)
    full_df = full_df.append(combine_df)
#     print(full_df)

# print(full_df)
full_df.to_csv("training-data-complete-8nov-trimmed.csv")


# In[ ]:





# In[ ]:




