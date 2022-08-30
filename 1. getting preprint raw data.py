#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 12:47:12 2022

@author: ben
"""

import paperscraper

from paperscraper.get_dumps import biorxiv, medrxiv, chemrxiv

medrxiv('medrxiv/medrxiv_raw_data.jsonl')

paperscraper.get_dumps