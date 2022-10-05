#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 14:10:08 2022

@author: ben
"""
import urllib.request
import urllib
import pandas as pd
pd.set_option('display.max_columns', 6)

# getting author names, and institutions from arxiv_id and doi

#%% #get arxiv_ids

article_citations_complete = pd.read_pickle(
    "data/cumulative_citatations_data.pkl")

arxiv_id_df = article_citations_complete.index.to_numpy()

doi_df = article_citations_complete.doi.reset_index().doi.to_csv("arxiv_published_dois_reduced.csv", index=False)



#%% 
arxiv_api_data = []
url = 'http://export.arxiv.org/api/query?id_list=cond-mat/0207270v1'
data = urllib.request.urlopen(url)
print(data.read().decode('utf-8'))


for i in len(arxiv_id_df)-1:
    temp_df = urllib.request.urlopen("http://export.arxiv.org/api/query?id_list="+arxiv_id_df[i])
    dataframes_list.append(data.read().decode('utf-8')))