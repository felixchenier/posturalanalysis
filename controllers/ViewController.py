# -*- coding: utf-8 -*-
"""
Created on Wed May 11 15:09:27 2022

@author: Tom
"""

from views.filebrowse import start
from views.MainView import MainWindow, openMainWindow


def OpenFile():
    path = start()
    return path
