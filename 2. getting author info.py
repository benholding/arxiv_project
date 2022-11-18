#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 14:10:08 2022

@author: ben
"""
#for data manipulation
import pandas as pd #importing the pandas library
import numpy as np #
pd.set_option('display.max_columns', 40) #setting an option for how many columns are shown in the console when loading dataframes
pd.set_option('display.width', 180) #this value can be changed to 

#for data visualisation
import matplotlib.pyplot as plt #importing the pyplot function from matplotlib and referring to it via plt
from matplotlib import rcParams #importing the rcParams function from matplotlib, because i wanted to have control over default plotting settings

plt.style.use("ggplot") #setting the plot style so that they look like ggplot...
rcParams['figure.figsize'] = (12,  6) #setting plot size in inches (width, height)


#%% #import citation information dataframe

article_citations_complete = pd.read_pickle(
    "data/cumulative_citatations_data.pkl") #here i load the citation data for preprints and published articles (data created using script 1.)

#%% import metadata about each published article -
#1. This data came from WoS after matching our doi information per published preprint
#2. We obtain not only article and author metadata but also...
#3. We get all publications each author ever published

published_article_metadata = pd.read_csv("./data/wos_data/arxiv_pubs.csv") #importing the csv containing 
variables_to_keep = ["doi_code", "author_seq", "cluster_id", "full_name", "gender", "orcid", "affiliation_seq", "affiliation_organization_enhanced_seq", "organization_enhanced_id", "organization_enhanced", "country", "is_industry", "collaboration_type_no"]
author_information = published_article_metadata[variables_to_keep]

#exploritory analysis of author information
author_information.info()
author_information.duplicated().sum() #we have 1071 rows that are duplicates - why?
author_information[author_information.duplicated(keep = False)] #using keep = False here to ensure it shows all instances of the duplicate
# uncertain why these duplicate authors exist, but we can remove them
author_information_2 = author_information[~author_information.duplicated(keep = 'first')] #~ inverts a logical variable
author_information_2.gender.value_counts()
author_information_2.organization_enhanced.value_counts()
author_information_2.country.value_counts()
author_information_2.is_industry.value_counts()
author_information_2.collaboration_type_no.value_counts()
author_information_2.gender.value_counts().plot(kind="bar")
#author_information_2.organization_enhanced.value_counts().plot(kind="bar")
author_information_2.country.value_counts().plot(kind="bar")

#creating dataset of first and last authors only
first_authors_info = author_information_2.loc[author_information_2['author_seq'] == 1].reset_index(drop = True)

#next i need to work out how to group by doi, so i can identify the max of the seq, and then use that to identify who the last authors were
last_author_seq_per_article = author_information_2.groupby('doi_code')['author_seq'].max().dropna().reset_index().rename(columns = {'author_seq': 'last_author_seq_in_article'})

author_information_2 = author_information_2.merge(last_author_seq_per_article, on = 'doi_code', how = 'left')
last_author_info = author_information_2[author_information_2['author_seq'] == author_information_2['last_author_seq_in_article']].reset_index(drop = True)

#sanity check that these are unique last authors
last_author_info[last_author_info.duplicated('doi_code', keep = False)] #duplicates due to multiple affilations - totally fine!


#%% import complete publication list
author_performance_indices_frac = pd.read_csv("./data/wos_data/arxiv_clusterID_impact_frac.csv")
author_performance_indices_frac = author_performance_indices_frac\
    .assign(pseudo_h = 0.54*np.sqrt(author_performance_indices_frac['p']*author_performance_indices_frac['mcs']))\
    .rename(columns = {'pub_set_no1': 'cluster_id'})
    
author_performance_indices_full = pd.read_csv("./data/wos_data/arxiv_clusterID_impact_full.csv")
author_performance_indices_full = author_performance_indices_full\
    .assign(pseudo_h = 0.54*np.sqrt(author_performance_indices_full['p']*author_performance_indices_full['mcs'])) 
    
median_full_pseudoh = np.median(author_performance_indices_full['pseudo_h'].dropna())
median_frac_pseudoh = np.median(author_performance_indices_frac['pseudo_h'].dropna())

plt.hist(author_performance_indices_frac.pseudo_h[author_performance_indices_frac.pseudo_h <= 2*np.std(author_performance_indices_frac.pseudo_h)], bins = 100, edgecolor = 'black')
plt.axvline(median_frac_pseudoh, color = 'yellow')
plt.title('Histgram of fractionalised pseudo h-index values')
plt.xlabel('Pseudo Fractionalised h-index (excluding >2 SD)')



    
plt.hist(author_performance_indices_full.pseudo_h[author_performance_indices_full.pseudo_h <= 2*np.std(author_performance_indices_full.pseudo_h)], bins = 100, edgecolor = 'black')
plt.axvline(median_full_pseudoh, color = 'yellow')
plt.title('Histgram of full pseudo h-index values')
plt.xlabel('Pseudo full h-index (excluding >2 SD)')
plt.ylabel('Number of authors')

#%%
# To do: Connect arkiv data to published articles metadata + first_author information and last_author information
article_citations_complete

author_performance_indices_full

test = first_authors_info[first_authors_info['affiliation_seq'] == 1.0][['doi_code', 'cluster_id', 'gender','organization_enhanced', 'country', 'affiliation_seq', 'affiliation_organization_enhanced_seq','organization_enhanced_id']]\
    .rename(columns = {'doi_code': 'doi', 'organization_enhanced': 'institution'})\
    .reset_index(drop= True)\
    .merge(article_citations_complete, on = 'doi', how = 'right')

#TODO: for some reason the number of rows has gone up! Why?? We need to find out what's going on
"""seems to be due to multiple affilations"""

test[test.duplicated('doi', keep = False)].head(n = 30)
"""it seems that individuals have multiple first affilations if there are multiple entries for the same university. For example, Kings college london and University of London. 
one way to potentially deal with it (or really just push the problem down the road), would be to have multiple columns per individual.
Another way, is to leave it. And then later try and join with the Leiden ranking, and keep those which we are able to do so (will likely need Jespers help for this. """


# seeing if there are any information about organisations if we don't actually ahve information about sequence order of affilations (at least per individual)
first_authors_info.query('affiliation_seq != affiliation_seq & organization_enhanced != organization_enhanced') #these are the same, the query function seems very useful (a bit like the R filter, since the pandas filter is only fow filtering based on index or row nuymber)
# so we see that if there is no affilation sequence, there is no informationa about the organisation
# Therefore we aren't losing any valuable information if we only include individuals where we know the affilation_seq


