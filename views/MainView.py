# -*- coding: utf-8 -*-
"""
Created on Thu May 12 16:42:37 2022

@author: Tom
partially inspired by tutorial at: https://www.pythonguis.com/tutorials/plotting-matplotlib/

and modifying some code form ktk
"""
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QApplication, QFileDialog, QGroupBox, QVBoxLayout, QDesktopWidget, QShortcut
import numpy as np
from PyQt5.uic import loadUi
from PyQt5.QtGui import QKeySequence
from models.MakeData import Data
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from controllers import DataController
from matplotlib.figure import Figure


class MainWindow(QtWidgets.QMainWindow):
    data: Data
    startBS = False
    peakBS = False
    phase1 = False
    maxAtteinte = False
    cid = None

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        loadUi('static/mainWindowTabbed.ui', self)

        # TAB1 Buttons
        self.openStudyButton.clicked.connect(self.findAStudySaveFile)
        self.saveLocation.clicked.connect(self.findASaveFile)
        self.browse.clicked.connect(self.findADataFile)

        # TAB2 Buttons
        self.save.clicked.connect(self.SaveButton)
        self.BSPhaseStart.clicked.connect(self.setStartBS)
        self.BSPeak.clicked.connect(self.setPeakBS)
        self.Phase1Start.clicked.connect(self.setPhase1)
        self.maxBtn.clicked.connect(self.setMax)

        # TAB2 Shortcuts
        self.shortcutStartBS = QShortcut(QKeySequence('Ctrl+1'), self.tabData)
        self.shortcutPeakBS = QShortcut(QKeySequence('Ctrl+2'), self.tabData)
        self.shortcutPhase1 = QShortcut(QKeySequence('Ctrl+3'), self.tabData)
        self.shortcutSave = QShortcut(QKeySequence('Ctrl+4'), self.tabData)

        self.shortcutStartBS.activated.connect(self.setStartBS)
        self.shortcutPeakBS.activated.connect(self.setPeakBS)
        self.shortcutPhase1.activated.connect(self.setPhase1)
        self.shortcutSave.activated.connect(self.SaveButton)

        # Initial Values
        self.rowSB.setValue(3)

    def plotData(self, dt: Data):
        self.populateCanvas(dt)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.sc)
        self.displayGB.setLayout(self.layout)
        self.show()

    def populateCanvas(self, dt: Data):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        df = dt.ts.to_dataframe()
        df.plot(ax=self.sc.axes)
        self.AddEventsToCanvas(dt)

    def findADataFile(self):
        if(self.filename.text() == ''):
            fname = QFileDialog.getOpenFileName(
                self, 'Open file', '', 'Excel files (*.xlsx *.xlsm *.xls)')
            self.filename.setText(fname[0])
            self.data = DataController.initialiseData(fname[0])
            self.plotData(self.data)
        else:
            fname = QFileDialog.getOpenFileName(
                self, 'Open file', '', 'Excel files (*.xlsx *.xlsm *.xls)')
            if(fname[0] != ''):
                self.filename.setText(fname[0])
                self.data = DataController.initialiseData(fname[0])
                self.replot(self.data)
            else:
                self.MessageWarning(
                    "Erreur - Impossible d'ouvrir le document sélectionné")

    def findASaveFile(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Open file', '', 'Excel files (*.xlsx)')
        self.savefilename.setText(fname[0])

    def findAStudySaveFile(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Open file', '', 'Excel files (*.xlsx)')
        self.groupSaveFileName.setText(fname[0])

    def replot(self, dt: Data):
        # Toolbar delete
        widget = self.layout.itemAt(0).widget()
        widget.deleteLater()

        # Canvas delete
        widget = self.layout.itemAt(1).widget()
        if(self.cid != None):
            self.sc.mpl_disconnect(self.cid)
            self.startBS = False
            self.peakBS = False
            self.phase1 = False
            self.maxAtteinte = False
        widget.deleteLater()

        self.BSPhaseStart.setDefault(False)
        self.BSPeak.setDefault(False)
        self.Phase1Start.setDefault(False)
        self.maxBtn.setDefault(False)

        self.populateCanvas(dt)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.sc)
        self.show()

    def onclick(self, event):
        time = event.xdata
        if(self.startBS):
            DataController.addBSPhaseStart(self.data, time)
            self.replot(self.data)

        elif(self.peakBS):
            DataController.addBSPhasePeak(self.data, time)
            self.replot(self.data)

        elif(self.phase1):
            DataController.addPhase1(self.data, time)
            self.replot(self.data)

        elif(self.maxAtteinte):
            DataController.addMaxAtteinte(self.data, time)
            self.replot(self.data)

    # This function is a modified version of the plot event
    # from ktk, modified to fit context

    def AddEventsToCanvas(self, dt: Data):
        n_events = len(dt.ts.events)
        event_times = []
        for event in dt.ts.events:
            event_times.append(event.time)

        if len(dt.ts.events) > 0:
            event_line_x = np.zeros(3 * n_events)
            event_line_y = np.zeros(3 * n_events)

            for i_event in range(0, n_events):
                event_line_x[3 * i_event] = event_times[i_event]
                event_line_x[3 * i_event + 1] = event_times[i_event]
                event_line_x[3 * i_event + 2] = np.nan

                event_line_y[3 * i_event] = dt.min_Y
                event_line_y[3 * i_event + 1] = dt.max_Y
                event_line_y[3 * i_event + 2] = np.nan

            self.sc.axes.plot(event_line_x, event_line_y, ':k')

            for event in dt.ts.events:
                if event.name == '_':
                    name = '_'
                else:
                    name = f"{event.name}"

                self.sc.axes.text(
                    event.time,
                    dt.max_Y,
                    name,
                    rotation='vertical',
                    horizontalalignment='center',
                    fontsize='small',)

    def setStartBS(self):
        if self.startBS == False:
            self.startBS = True
            self.peakBS = False
            self.maxAtteinte = False
            self.phase1 = False
            self.cid = self.sc.mpl_connect('button_press_event', self.onclick)
            self.BSPhaseStart.setDefault(True)
        else:
            self.startBS = False
            self.sc.mpl_disconnect(self.cid)
            self.BSPhaseStart.setDefault(False)

    def setPeakBS(self):
        if self.peakBS == False:
            self.startBS = False
            self.maxAtteinte = False
            self.peakBS = True
            self.phase1 = False
            self.cid = self.sc.mpl_connect('button_press_event', self.onclick)
            self.BSPeak.setDefault(True)

        else:
            self.peakBS = False
            self.sc.mpl_disconnect(self.cid)
            self.BSPeak.setDefault(False)

    def setPhase1(self):
        if self.phase1 == False:
            self.startBS = False
            self.peakBS = False
            self.maxAtteinte = False
            self.phase1 = True
            self.cid = self.sc.mpl_connect('button_press_event', self.onclick)
            self.Phase1Start.setDefault(True)

        else:
            self.phase1 = False
            self.sc.mpl_disconnect(self.cid)
            self.Phase1Start.setDefault(False)

    def setMax(self):
        if self.maxAtteinte == False:
            self.startBS = False
            self.peakBS = False
            self.phase1 = False
            self.maxAtteinte = True
            self.cid = self.sc.mpl_connect('button_press_event', self.onclick)
            self.maxBtn.setDefault(True)

        else:
            self.maxAtteinte = False
            self.sc.mpl_disconnect(self.cid)
            self.maxBtn.setDefault(False)

    def SaveButton(self):
        dataPath = self.savefilename.text()
        groupPath = self.groupSaveFileName.text()
        subject = self.subjectnameEdit.text()
        length = self.footWidthDSB.value()
        width = self.footLengthDSB.value()

        groupTick = self.studyFormatCB.isChecked()

        if(dataPath == '' or groupPath == ''):
            self.MessageWarning(
                'Il manque des emplacements de sauvegarde, SVP les entrer dans Informations avant de recommencer')
            self.tabWidget.setCurrentIndex(0)

        elif(length == 0.0 or width == 0.0):
            self.MessageWarning(
                'Les dimensions des pieds sont invalides, svp les entrer avant de recommencer')
            self.tabWidget.setCurrentIndex(0)

        elif(subject == ''):
            self.MessageWarning(
                'SVP Identifier le participant avant de continuer')
            self.tabWidget.setCurrentIndex(0)

        else:
            self.data.footLength = length
            self.data.footWidth = width

            if(self.newsave.isChecked()):
                DataController.SaveToNewDocument(
                    self.data, dataPath)
            else:
                DataController.SaveToExistingDocument(
                    self.data, singleDataPath=dataPath)

            if(groupTick):
                DataController.NewGroupDocument(
                    self.data, groupDataPath=groupPath)
            DataController.SaveToExistingGroupDocument(
                self.data, groupDataPath=groupPath, rowToWrite=self.rowSB.value(), participant=subject)

            self.SaveComplete()

    def MessageWarning(self, message: str):
        dialog = QMessageBox(self)
        dialog.setWindowTitle('Erreur')
        dialog.setText(message)
        dialog.exec()

    def GetGroupPath(self):
        return self.groupSaveFileName.text()

    def SaveComplete(self):
        self.newsave.setChecked(False)
        self.studyFormatCB.setChecked(False)
        self.tabWidget.setCurrentIndex(0)


def openMainWindow():
    tempApp = QApplication(sys.argv)
    tempApp.setQuitOnLastWindowClosed(True)
    mw = MainWindow()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mw)
    widget.show()
    tempApp.exec_()


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        
