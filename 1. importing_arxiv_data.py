#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 13:07:02 2022

@author: ben
"""

# analysis of arxiv data (from Traag, QSS, 2021)

import os
import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', 6)

#%%
# Read data

files = os.listdir("./data/arxiv")
file_count = len(files)

# create empty list
dataframes_list = []
 
# append datasets to the list
for i in range(file_count):
    temp_df = pd.read_csv("./data/arxiv/"+files[i], 
                          dtype={'arxiv_id': str})
    dataframes_list.append(temp_df)


citations_by_day = dataframes_list[1][
    pd.notnull(dataframes_list[1]['date']) & pd.notnull(dataframes_list[1]['cit_day'])
    ] #removing NAs in date published and citation 
citations_by_day['arxiv_id'] = citations_by_day['arxiv_id'].str.lower()
    

#%%
# Read link between arxiv and doi and meta data
arxiv_doi_df = dataframes_list[2]

arxiv_doi_df['arxiv_id'] = arxiv_doi_df['arxiv_id'].str.lower()
arxiv_doi_df['doi'] = arxiv_doi_df['doi'].str.lower()
arxiv_doi_df['preprint_days'] = arxiv_doi_df['preprint_days'].astype(int)

arxiv_doi_df_reduced = arxiv_doi_df[(arxiv_doi_df['preprint_days'] >= 365) & (arxiv_doi_df['publication_date'] <= '2016-12-31')] #keeping only preprints that were preprints for a year before being published and articles that had 1 year to collect citations
plt.hist(arxiv_doi_df_reduced.pre_publication_n_cit,100)
plt.hist(arxiv_doi_df_reduced.post_publication_n_cit, 100)


#%%
# combining the two dataframes

preprint_info = arxiv_doi_df_reduced.drop(columns = ['doi', 'preprint_days', 'srcid'])
desired_arxiv_ids_only = arxiv_doi_df_reduced['arxiv_id']

citations_by_day_reduced = citations_by_day[citations_by_day['arxiv_id'].isin(desired_arxiv_ids_only)]
merged_two_datasets = citations_by_day_reduced\
    .merge(preprint_info, on = 'arxiv_id', how = 'left')\
    .rename(columns = {'cit_day': 'days_from_preprint_posted'})\
    .sort_values(by = ['arxiv_id', 'date'])

merged_two_datasets[['date', 'preprint_date', 'publication_date']] = merged_two_datasets[['date', 'preprint_date', 'publication_date']].apply(pd.to_datetime)

merged_two_datasets['days_from_publication'] = (merged_two_datasets.date - merged_two_datasets.publication_date).dt.days
        
preprint_citations_year1 = merged_two_datasets[(merged_two_datasets['days_from_preprint_posted'] <= 365)]
postprint_citations_year1 = merged_two_datasets[(merged_two_datasets['days_from_publication'] >= 0) & (merged_two_datasets['days_from_publication'] <= 365)]

preprint_citations_year1_totalcounts = preprint_citations_year1\
    .groupby('arxiv_id')\
    .agg({'doi': 'first', 'cit': 'sum', 'preprint_date': 'first', 'publication_date': 'first'})\
    .sort_values('cit', ascending = False)\
    .rename(columns = {'cit': 'preprint_citations_1styear'})
    
postprint_citations_year1_totalcounts = postprint_citations_year1\
     .groupby('arxiv_id')\
     .agg({'doi': 'first', 'cit': 'sum', 'preprint_date': 'first', 'publication_date': 'first'})\
     .sort_values('cit', ascending = False)\
     .rename(columns = {'cit': 'postprint_citations_1styear'})

cumulative_dataset = postprint_citations_year1_totalcounts\
    .merge(preprint_citations_year1_totalcounts, on = ['arxiv_id', 'doi', 'preprint_date', 'publication_date'], how = 'outer' )\
    .reset_index()\
    .fillna(0)


#i need to make two dataframes - a) one with articles with recieved citations, but not in the 1 year window, and b) one of the articles (combined preprint and postprint) that never recieved any citations
#a)
arxiv_ids_no_citesfirstyear = pd.DataFrame(citations_by_day_reduced.arxiv_id[~citations_by_day_reduced.arxiv_id.isin(cumulative_dataset.arxiv_id)]).drop_duplicates()
no_cites_first_year = arxiv_ids_no_citesfirstyear.merge(arxiv_doi_df_reduced, on = 'arxiv_id', how = 'left')\
    .assign(postprint_citations_1styear = 0, preprint_citations_1styear = 0)\
    .filter(items = cumulative_dataset.columns)
    
cumulative_dataset_with_nocitesfirstyear = pd.concat([cumulative_dataset, no_cites_first_year])
#b)
#which of the arxiv_ids were in preprint_info but not in cumulative_dataset_with_nocitesfirstyear

arxiv_ids_no_cites_ever = pd.DataFrame(preprint_info.arxiv_id[~preprint_info.arxiv_id.isin(cumulative_dataset_with_nocitesfirstyear.arxiv_id)])
no_cites_ever = arxiv_ids_no_cites_ever.merge(arxiv_doi_df_reduced, on = 'arxiv_id', how = 'left')\
    .assign(postprint_citations_1styear = 0, preprint_citations_1styear = 0)\
    .filter(items = cumulative_dataset.columns)
    
article_citations_complete = pd.concat([cumulative_dataset_with_nocitesfirstyear, no_cites_ever]).sort_values('preprint_citations_1styear', ascending = False)\
    .set_index('arxiv_id')

#%% # saving final dataset
article_citations_complete.to_pickle("data/cumulative_citatations_data.pkl")
