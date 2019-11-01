#!/usr/bin/env python
# coding: utf-8

# In[3]:

from glob import glob 
import pandas as pd

files = glob('./data/raw/*.csv')

for path in files:
    
    # TODO: fix column names
    colNames=['index', 'x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'x3', 'y3', 'z3', 
              'x4', 'y4', 'z4', 'x5', 'y5', 'z5', 'nan', 'class', 'null', 'index'] 
    dataset = pd.read_csv(path, names=colNames, header=None)
    dataset = dataset.drop(columns=['x4', 'y4', 'z4', 'x5', 'y5', 'z5', 'nan', 'null', 'index'])

    # remove index 
    df = dataset.groupby('class')

    first = "raw\\"
    last = "-processed.csv"
    start = path.index(first) + len(first)
    end = path.index(last, start)
    name = path[start:end]
    
    for x in df.groups:
        groupName = x
        df.get_group(x).to_csv("./data\individual/" + name + "-" + groupName +".csv")
        


