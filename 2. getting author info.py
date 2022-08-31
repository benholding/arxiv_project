#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 14:10:08 2022

@author: ben
"""

# getting author names, and institutions from arxiv_id and doi

#%% #get cumulative citations data

article_citations_complete = pd.read_pickle("data/cumulative_citatations_data.pkl")

