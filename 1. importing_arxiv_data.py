#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 13:07:02 2022

Author: Benjamin C. Holding
Overview: In this script, I import the data from V. Traag's 2021 paper' https://direct.mit.edu/qss/article/2/2/496/98105/Inferring-the-causal-effect-of-journals-on 
I then do some data cleaning, and save all the datafiles within a single "pickle .pkl" file. 

"""
#setup

import os #to work with file structures
import pandas as pd #to manipulate data
import matplotlib.pyplot as plt #for creating histograms
pd.set_option('display.max_columns', 6) #trying to get columns to display nicer in spyder

#%%
"""
In this first bit of code, I use a for loop to put all of our csv data from the data/arxiv folder, and then save them all within a list.
"""

files = os.listdir("./data/arxiv") #get list of file names
file_count = len(files) #how many files are there?

# create empty list
dataframes_list = [] #initialising list to save DFs into
 
# append datasets to the list
for i in range(file_count): #for each csv file in the folder
    temp_df = pd.read_csv("./data/arxiv/"+files[i],  #read the file and save within a temporary file
                          dtype={'arxiv_id': str}) #making sure to save arxiv_id as a string rather than a number
    dataframes_list.append(temp_df) #then add that temp DF to the list


citations_by_day = dataframes_list[1][ #here I pull out a specific DF from the list (actually it turned out that working with lists was not so smooth)
    pd.notnull(dataframes_list[1]['date']) & pd.notnull(dataframes_list[1]['cit_day']) #keeping only rows of per-day citation info if we have no NAs in date published and citation 
    ] 
citations_by_day['arxiv_id'] = citations_by_day['arxiv_id'].str.lower() #within the same DF as above, i make sure all charectors are lower case for arxiv_id
    

#%%
# Next we wanted to get a list of DOIs that could be matched with information stored in the CWTS WoS database
arxiv_doi_df = dataframes_list[2] #saving the appropriate element of the list as a seperate object.

arxiv_doi_df['arxiv_id'] = arxiv_doi_df['arxiv_id'].str.lower() #Like I did before, i'm making sure all arxiv_id strings are lowercase
arxiv_doi_df['doi'] = arxiv_doi_df['doi'].str.lower() #same with dois
arxiv_doi_df['preprint_days'] = arxiv_doi_df['preprint_days'].astype(int) #setting the datatype of the preprint days variable to integer

arxiv_doi_df.doi.drop_duplicates().to_csv("arxiv_published_dois.csv", index=False) #saving a list of unique dois as a csv file
arxiv_doi_df_reduced = arxiv_doi_df[(arxiv_doi_df['preprint_days'] >= 365) & (arxiv_doi_df['publication_date'] <= '2016-12-31')] #keeping only preprints that were preprints for a year before being published and articles that had 1 year to collect citations

plt.hist(arxiv_doi_df_reduced.pre_publication_n_cit,100) #just out of interest, making some histograms to show the distribution of citations obtained before ...
plt.hist(arxiv_doi_df_reduced.post_publication_n_cit, 100) # ... and after publication.


#%%
# The ultimate aim of this step was to create a DF (called article_citations_complete) where we have per arxiv_id, information regarding:
# published doi, date of preprint publication, date of actual publication, number of preprint citations obtained in it's first year as a preprint, number of citations obtained in first year as a actual published article

preprint_info = arxiv_doi_df_reduced.drop(columns = ['doi', 'preprint_days', 'srcid']) #first extracting key info regarding each preprint
desired_arxiv_ids_only = arxiv_doi_df_reduced['arxiv_id'] #extracting which arxiv_ids we are interested in analysing (as commented above, we are only interested in preprints that were preprints for a year before being published and articles that had 1 year to collect citations)


citations_by_day_reduced = citations_by_day[citations_by_day['arxiv_id'].isin(desired_arxiv_ids_only)] #then, obtaining citation information only for the eligible arxiv_ids

merged_two_datasets = (citations_by_day_reduced #then, combining the citation data with information about the preprints
    .merge(preprint_info, on = 'arxiv_id', how = 'left') #doing a left_join
    .rename(columns = {'cit_day': 'days_from_preprint_posted'}) #renaming a column
    .sort_values(by = ['arxiv_id', 'date'])) #arranging the values

merged_two_datasets[['date', 'preprint_date', 'publication_date']] = (merged_two_datasets[['date', 'preprint_date', 'publication_date']]
                                                                      .apply(pd.to_datetime)) #making sure all the date variables are in pandas datatime format

merged_two_datasets['days_from_publication'] = (merged_two_datasets.date - merged_two_datasets.publication_date).dt.days #i think this is just extracting the days difference between preprint and publication dates
        
preprint_citations_year1 = merged_two_datasets[(merged_two_datasets['days_from_preprint_posted'] <= 365)] #now we make two DFs, one with the citation information up to 365 days after publication of the preprint (i.e. preprints). Since all preprints needed to be preprints for at least a year (see above) then this is only preprint data...
postprint_citations_year1 = merged_two_datasets[(merged_two_datasets['days_from_publication'] >= 0) & (merged_two_datasets['days_from_publication'] <= 365)] #and another for citation information from day 0 to day 365 after publication

preprint_citations_year1_totalcounts = (preprint_citations_year1 #here i'm caluclating the total citation counts (agregating over the daily data) for the preprints 
    .groupby('arxiv_id') #grouping by arxiv_id
    .agg({'doi': 'first', 'cit': 'sum', 'preprint_date': 'first', 'publication_date': 'first'}) #then deciding how groups should be summarised. doi and dates we take the first (since they are all the same), we sum citations, 
    .sort_values('cit', ascending = False) #sorting the DF by citations
    .rename(columns = {'cit': 'preprint_citations_1styear'})) #and renaming the citations variable
    
postprint_citations_year1_totalcounts = (postprint_citations_year1 #doing the same as above but for postprints
     .groupby('arxiv_id')
     .agg({'doi': 'first', 'cit': 'sum', 'preprint_date': 'first', 'publication_date': 'first'})
     .sort_values('cit', ascending = False)
     .rename(columns = {'cit': 'postprint_citations_1styear'}))

cumulative_dataset = (postprint_citations_year1_totalcounts #now merging together preprint and publication citation information
    .merge(preprint_citations_year1_totalcounts, on = ['arxiv_id', 'doi', 'preprint_date', 'publication_date'], how = 'outer' ) # keeping all rows from both DFs
    .reset_index()
    .fillna(0)) #in places where there are NAs, these are filled with zero (since all articles are eligible)

#We now have a nice dataset, however we may be missing articles that either a) articles that recieved citations but not within the year we are interested in b) never recieved any citations (either as a preprint or as a published article)

#Therefore, first we find the articles that didn't get any citations in the first year
#the strategy is to look for arxiv_ids that were in the citations_by_day_reduced DF but not in the cumulative_dataset DF
arxiv_ids_no_citesfirstyear = pd.DataFrame(citations_by_day_reduced.arxiv_id[~citations_by_day_reduced.arxiv_id.isin(cumulative_dataset.arxiv_id)]).drop_duplicates() #we get a list of missing arxiv_ids

#then we make a mini DF that matches the structure of the cumulative_dataset DF
no_cites_first_year = (arxiv_ids_no_citesfirstyear
                       .merge(arxiv_doi_df_reduced, on = 'arxiv_id', how = 'left')
                       .assign(postprint_citations_1styear = 0, preprint_citations_1styear = 0) #setting citations to be zero
                       .filter(items = cumulative_dataset.columns))

#Then we can row bind (Concatenate) the two:    
cumulative_dataset_with_nocitesfirstyear = pd.concat([cumulative_dataset, no_cites_first_year])

#b) The next issue was finding articles that were never cited #
#The strategy is to look for which of the arxiv_ids were in preprint_info but not in cumulative_dataset_with_nocitesfirstyear

arxiv_ids_no_cites_ever = pd.DataFrame(preprint_info.arxiv_id[~preprint_info.arxiv_id.isin(cumulative_dataset_with_nocitesfirstyear.arxiv_id)]) #again we get a list of arxiv_ids
no_cites_ever = (arxiv_ids_no_cites_ever #again making a DF that matches the structure of the cumulative_dataset DF
                 .merge(arxiv_doi_df_reduced, on = 'arxiv_id', how = 'left')
                 .assign(postprint_citations_1styear = 0, preprint_citations_1styear = 0)
                 .filter(items = cumulative_dataset.columns))
    
article_citations_complete = (pd.concat([cumulative_dataset_with_nocitesfirstyear, no_cites_ever]) #again concatenating the two DFs
                                .sort_values('preprint_citations_1styear', ascending = False)
                                .set_index('arxiv_id')
                                .sort_values(['postprint_citations_1styear','preprint_citations_1styear', 'arxiv_id'], ascending = False))

#%% # saving final dataset
article_citations_complete.to_pickle("data/cumulative_citatations_data.pkl") #saving the data in python format
