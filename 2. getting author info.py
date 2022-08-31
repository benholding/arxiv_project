#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 14:10:08 2022

@author: ben
"""
import urllib.request
import urllib

# getting author names, and institutions from arxiv_id and doi

#%% #get cumulative citations data


article_citations_complete = pd.read_pickle(
    "data/cumulative_citatations_data.pkl")

url = 'http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1'
 data = urllib.request.urlopen(url)
   print(data.read().decode('utf-8'))
