#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 13:34:35 2022

@author: ben
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
###

preprints = pd.read_csv(r'/Users/ben/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofCopenhagen/UCPH_NielsenSociologyGroup - Documents/Carlsberg Project/Projects/Pre-print/preprint_Rproject/final_dataset.csv')
#%%

len(preprints.drop_duplicates('author_id')) #514316 - this is only the number of first author authors actually
len(preprints.drop_duplicates('author_id')[preprints.drop_duplicates('author_id').is_consortium == True]) #1582 consortium authors
len(preprints.drop_duplicates('author_id')[preprints.drop_duplicates('author_id').highly_cited_author == True]) #1582 highly cited authors

#number of preprints

len(preprints.drop_duplicates('preprint_id')) #119214
len(preprints.drop_duplicates('preprint_id')[preprints.drop_duplicates('preprint_id').repo == 'biorxiv']) #From biorxiv = 105045
len(preprints.drop_duplicates('preprint_id')[preprints.drop_duplicates('preprint_id').repo == 'medrxiv']) #From medrxiv = 14169

# number of single author papers
len(preprints.drop_duplicates('preprint_id')[(preprints.drop_duplicates('preprint_id').is_first_author == True) & (preprints.drop_duplicates('preprint_id').is_last_author == True)]) #3593

#number of institutions
len(preprints.drop_duplicates('institution')) #161157

# number of institutions matched to grid
preprints.drop_duplicates('institution').grid_id.isna().sum() #36243 NAs
preprints.drop_duplicates('institution').grid_id.count() #801520 non-NAs
plt.hist(preprints.drop_duplicates('institution').grid_id.value_counts(), 100)

#number of countries
len(preprints.drop_duplicates('country_allsources').country_allsources.dropna()) #188 countries

#number of preprints published
len(preprints.drop_duplicates('preprint_id').published_in_which_journal.dropna()) #45858

#### #selecting only published in journals of interest
published_preprints = preprints[preprints.preprint_is_published == 1]
len(published_preprints.drop_duplicates('preprint_id')) #45863
list_of_journals = preprints.drop_duplicates('preprint_id').value_counts('matched_journal_name')
list_of_journals_to_match = 




