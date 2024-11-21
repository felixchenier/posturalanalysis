# -*- coding: utf-8 -*-
"""
Created on Mon May  9 17:34:04 2022

@author: Tom
"""

import pandas as pd


def init_dataframe(path):
    df = pd.read_excel(path)
    return df

def get_column_at(df, index):
    return df.iloc[:, index-1:index]

def get_title_at(df, index):
    return df.columns[index-1]

