#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 14:10:08 2022

@author: ben
"""
import pandas as pd
pd.set_option('display.max_columns', 6)

# getting author names, and institutions from arxiv_id and doi

#%% #get arxiv_ids

article_citations_complete = pd.read_pickle(
    "data/cumulative_citatations_data.pkl")

arxiv_id_df = article_citations_complete.index.to_numpy()

doi_df = article_citations_complete.doi.reset_index().doi.to_csv("arxiv_published_dois_reduced.csv", index=False)

#after doing the above, we extracted information from Web of Science by matching the dois to metadata in the database

#%% import metadata about each published article

published_article_metadata = pd.read_csv("./data/wos_data/arxiv_pubs.csv")
author_complete_publications = pd.read_csv("./data/wos_data/arxiv_clusterID_impact_frac.csv")
