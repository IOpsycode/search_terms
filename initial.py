# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 13:36:42 2019

@author: auracoll

Looking to investigate the data and determine what solution
is needed for quickest baseline work
for SG meeting on 6/4 and then legal team demo on 6/7

NEED TO DECIDE TO CAT INSIDE OR PRIOR TO DATAFRAME
"""

import os
import pandas as pd


def get_words(filepath):
    """
    get word list as a set from specified file path

    Parameters:
        path:   STRING of excel filepath
            NOTE this expects all words to be in first column

    Return: lower_case set of words
    """
    # get word list
    words = pd.read_excel(filepath, header=None, squeeze=True)
    # create set
    searchwords = set(words.str.lower())
    # return
    return searchwords


def get_ext(path, ext='.txt'):
    """
    get file paths that end in .txt

    Parameters:
        path:   STRING of direcory to search
            NOTE will crawl through all subdirectories
        ext:    STRING of extension to look for

    Return: list of filenames
    """

    files = []

    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if ext in file:
                files.append(os.path.join(r, file))
    return files


def make_df(files, searchwords):
    # create empty list of dataframes
    badfiles = []

    dfs = {}
    for file in files:
        try:
            text = open(file, encoding='utf-8').read()
            dfs[file] = text
        except(UnicodeDecodeError):
            print('Unicode Error at: ', str(file))
            badfiles.append(file)

    # convert to df
    df = pd.DataFrame([dfs]).T.reset_index()

    # name columns
    df.columns = ['LongFilename', 'Text']

    # save just ending of filename to join on
    df['filename'] = df['LongFilename'].str.split(
            '.pdf').str[0].str.split(
                    'Customer Agreements\\\\').str[1]

    # groupby the filename to concat the text
    grouped = df.groupby('filename').agg(lambda x: ' '.join(x)).reset_index()

    # create column of matches between search terms and text
    # NOTE text cannot be a set because multi-word searches
    grouped['matches'] = grouped['Text'].str.lower().apply(
            lambda x: [i for i in searchwords if i in x])
    # only save useful columns for end-user
    outdf = grouped[['filename', 'matches']].copy()
    # split filename to see parent directory for easier searching
    outdf['Directory Name'] = outdf['filename'].str.split('\\').str[0]
    # re-order columns
    outdf = outdf[['Directory Name', 'filename', 'matches']]
    # show column for each word that is matched somewhere in the text
    final = pd.concat(
            [outdf, outdf['matches'].str.join(
                    sep='*').str.get_dummies(sep='*')], axis=1)
    return final

# =============================================================================
# ############################### MAIN #######################################
# =============================================================================


files = get_ext('data/', ext='.txt')
searchwords = get_words('data/Search Terms.xlsx')
final = make_df(files=files, searchwords=searchwords)
final.to_csv('output/custom.csv', index=False)
