# -*- coding: utf-8 -*-
"""
Created on Mon May  9 18:58:41 2022

@author: Tom
"""

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi




class BrowseFile(QDialog):
    filePath = ''
    
    def __init__(self):
        super(BrowseFile, self).__init__()
        loadUi('static/filefinder.ui', self)
        self.browse.clicked.connect(self.findAFile)
        
    def findAFile(self):
        fname=QFileDialog.getOpenFileName(self, 'Open file', '', 'Excel files (*.xlsx)')
        self.filename.setText(fname[0])
        self.filePath =  fname[0]
    

        

def start():
    tempApp = QApplication(sys.argv)
    tempApp.setQuitOnLastWindowClosed(True)
    browsefile=BrowseFile()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(browsefile)
    widget.setFixedWidth(400)
    widget.setFixedHeight(300)
    widget.show()
    tempApp.exec_()
    return browsefile.filePath


