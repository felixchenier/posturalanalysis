# -*- coding: utf-8 -*-
"""
Created on Mon May  9 16:36:01 2022

@author: Tom
"""

import kineticstoolkit.lab as ktk
import numpy as np
from models.Loader import init_dataframe, get_title_at, get_column_at

FREQUENCY = 200  # Hz
INTERVAL = 1 / FREQUENCY  # s
FILTER = 10  # Hz
BS_START_NAME = 'Debut du backshift'
BS_PEAK_NAME = 'Peak du BS'
PHASE_1_NAME = 'Phase 1'
PHASE_2_NAME = 'Phase 2'
PHASE_1_2_TRANSITION_NAME = 'Phase 1 - Phase 2'


def Load(newPath):
    df = init_dataframe(newPath)
    return df


def CreateTS(newPath):
    df = Load(newPath)
    ts = ktk.TimeSeries()

    i = 1
    while i <= df.columns.size:
        title = str(get_title_at(df, i)).lower()
        ts.data[title] = get_column_at(df, i).to_numpy()
        strlist = title.split()
        ts.add_data_info(str(i), 'column name', strlist, in_place=True)
        i += 1

    ts.time = np.arange(0, (df.size / 2) * INTERVAL, INTERVAL)

    ts = FilterTS(ts)

    return ts


def FilterTS(ts: ktk.TimeSeries):
    temp = ktk.filters.butter(ts, fc=FILTER, filtfilt=True)
    return temp


def QuickShow(ts: ktk.TimeSeries):
    ts.plot()


class Data():

    TABLE = ['Moyenne (cm)',  # 0
             'Écart Type (cm)',  # 1
             'Étendue (cm)',  # 2
             'Max pr QS (cm)',  # 3
             'N Max pr QS (cm)',  # 4
             'Max - Moyenne (cm)',  # 5
             'ABS Max pr QS (cm)',  # 6
             'Atteinte :',  # 7
             'Durée (s)',  # 8
             'Amplitude (cm)',  # 9
             'Pente (cm/s)',  # 10
             'Vitesse :',  # 11
             'Moyenne (cm/s)',  # 12
             'Écart-Type (cm/s)',  # 13
             'Max (cm/s)',  # 14
             "Vitesse de l'atteinte:",  # 15
             'Durée entre atteinte et max (s)',  # 16
             'Distance entre atteinte et max (cm)'  # 17
             ]

    ts: ktk.TimeSeries
    footLength = 23.5
    footWidth = 12.5
    max_Y = 0
    min_Y = 0
    savelist = []

    # Bools to classify where to save data
    mainAxis = False  # True for y, false for x
    direction = False  # False for av and for g, True for arr and d
    eyesOpen = False  # True for open eyes, false for closed eyes + foam

    def __init__(self, ts: ktk.TimeSeries):
        self.ts = ts
        titles = self.GetDataArguments(1)
        self.SetDataInformations(titles)

        keys = ts.data.keys()
        for key in keys:
            values = ts.data[key]
            maxY = values.max()
            minY = values.min()

            if(maxY >= self.max_Y):
                self.max_Y = maxY
            if(minY <= self.min_Y):
                self.min_Y = minY

        self.savelist = self.CreateSaveList()

    def CreateSaveList(self):
        saveList = []
        i = 1
        while (i < 11):
            page = []
            saveList.append(page)
            i += 1
        return saveList

    # Input: column number, starting at 1

    def GetDataArguments(self, columnNumber: int):
        titles = self.ts.data_info[str(columnNumber)]['column name']
        return titles

    def SetDataInformations(self, titles):
        for value in titles:
            if value == 'yo' or value == 'yo+d':
                self.eyesOpen = True

            if value == 'av':
                self.mainAxis = True
                self.direction = False

            if value == 'arr':
                self.mainAxis = True
                self.direction = True

            if value == 'g':
                self.mainAxis = False
                self.direction = False

            if value == 'd':
                self.mainAxis = False
                self.direction = True

    def AddEvent(self, eventName: str, time: float):
        self.ts.add_event(time, eventName, in_place=True)

    # Input: column number, starting at 1

    def IsColumnMainAxis(self, value):
        titles = self.GetDataArguments(value)
        for value in titles:
            if value == 'ap':
                return (self.mainAxis == True)

            if value == 'ml':
                return (self.mainAxis == False)

    def Average(self, ts: ktk.TimeSeries):
        keys = ts.data.keys()
        averages = []
        for key in keys:
            values = ts.data[key]
            average = np.average(values)
            averages.append(average)
        return averages

    def CalculateSTD(self, ts: ktk.TimeSeries):
        keys = ts.data.keys()
        ets = []
        for key in keys:
            values = ts.data[key]
            et = np.std(values)
            ets.append(et)
        return ets

    def CalculateExtent(self, ts: ktk.TimeSeries):
        keys = ts.data.keys()
        extent = []
        for key in keys:
            values = ts.data[key]
            maxVal = np.max(values)
            minVal = np.min(values)
            extent.append(maxVal - minVal)
        return extent

    def MaxByQS(self, qs: float, ts: ktk.TimeSeries):
        keys = ts.data.keys()
        maxByQS = []
        for key in keys:
            values = ts.data[key]
            maxVal = np.max(values)
            maxByQS.append(maxVal - qs)
        return maxByQS

    def AbsoluteMaxByQS(self, qs: float, ts: ktk.TimeSeries):
        keys = ts.data.keys()
        maxByQS = []
        for key in keys:
            values = ts.data[key]
            maxVal = np.max(values)
            maxByQS.append(abs(maxVal - qs))
        return maxByQS

    def AverageByQS(self, qs: float, average: float):
        return average - qs

    def DiffMaxAverageByQS(self, maxByQs: float, average: float):
        return maxByQs - average

    def Time(self, ts: ktk.TimeSeries):
        length = len(ts.time)
        return ts.time[length - 1] - ts.time[0]

    def TimeAttMax(self, ts: ktk.TimeSeries):
        indexMax = ts.get_index_at_event("Maximum", 0)
        indexStart = ts.get_index_at_event(PHASE_1_NAME, 0)
        return ts.time[indexMax] - ts.time[indexStart]

    def DistMaxAtt(self, ts: ktk.TimeSeries):
        
        indexMax = ts.get_index_at_event("Maximum", 0)
        indexStart = ts.get_index_at_event(PHASE_1_NAME, 0)

        results = []
        keys = ts.data.keys()
        for key in keys:
            values = ts.data[key]
            maxV = values[indexMax]
            startV = values[indexStart]

            results.append(maxV - startV)
        return results

    def Amplitude(self, ts: ktk.TimeSeries):
        keys = ts.data.keys()
        amp = []
        for key in keys:
            values = ts.data[key]
            maxVal = np.max(values)
            minVal = np.min(values)
            amp.append(abs(maxVal - minVal))
        return amp

    def Pente(self, ts: ktk.TimeSeries, temps: float):
        keys = ts.data.keys()
        pentes = []
        for key in keys:
            values = ts.data[key]
            length = len(values)
            initial = values[0]
            final = values[length-1]
            pentes.append((final - initial) / temps)
        return pentes

    def GetSpeedTS(self):
        speedTS = self.ts.copy()
        keys = speedTS.data.keys()

        for key in keys:
            values = speedTS.data[key]
            size = len(values)

            i = 0
            while(i < size - 2):
                values[i] = abs((values[i] - values[i + 2]) / 0.01)
                i += 1

            index = [size - 2, size - 1]
            values = np.delete(values, index)
            speedTS.data[key] = values

        timeLen = len(speedTS.time)
        speedTS.time = np.delete(speedTS.time, [timeLen - 2, timeLen - 1])

        return speedTS

    def GetGroupedTS(self):
        return self.ts.get_ts_between_events(PHASE_1_NAME, PHASE_2_NAME, inclusive=True)

    # Function that returns corresponding ts based on event names from sheet number

    def TSDataSubset(self, sheetNumber: int, atteinte=False, ts=ktk.TimeSeries()):
        if(ts == ktk.TimeSeries()):
            ts = self.ts
        if(sheetNumber < 3):  # Phase 2
            return ts.get_ts_between_events(PHASE_1_2_TRANSITION_NAME, PHASE_2_NAME, inclusive=True)
        elif(sheetNumber < 5 and atteinte):  # Atteinte
            return ts.get_ts_between_events(BS_PEAK_NAME, PHASE_1_NAME, inclusive=True)
        elif(sheetNumber < 5 and not atteinte):  # Phase 1
            return ts.get_ts_between_events(PHASE_1_NAME, PHASE_1_2_TRANSITION_NAME, inclusive=True)
        else:  # Backshift
            return ts.get_ts_between_events(BS_START_NAME, BS_PEAK_NAME, inclusive=True)

    # This function takes in a sheet number and returns a int list to inform
    # which data needs to be calculated for save

    def SingleSaveDataFormat(self, sheetNumber: int):
        if(sheetNumber % 2 == 0):
            if sheetNumber == 4:
                return [0, 1, 2, 11, 12, 13, 14, 7, 8,  9, 10, 15, 12, 13, 14]
            else:
                return [0, 1, 2, 11, 12, 13, 14]
        elif(sheetNumber == 1):
            return [0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14]
        elif(sheetNumber == 3):
            return [0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 7, 8, 9, 10, 15, 12, 13, 14]
        elif(sheetNumber == 5):
            return [0, 1, 2, 8, 11, 12, 13, 14]
        elif(sheetNumber == 7):
            return [0, 1, 2, 16, 17]
        else:
            return []

    def GroupSaveDataFormat(self, sheetNumber: int):
        if(sheetNumber % 2 == 0):
            return [0, 1, 2, 11, 12, 13, 14]
        elif(sheetNumber == 1):
            return [0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14]
        elif(sheetNumber == 3):
            return [0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14]
        elif(sheetNumber == 5):
            return [0, 1, 2, 8, 11, 12, 13, 14]
        elif(sheetNumber == 7):
            return [0, 1, 2, 16, 17]
        elif(sheetNumber == 9):
            return [7, 8, 9, 10, 15, 12, 13, 14]

    def DataListToText(self, value: int):
        return self.TABLE[value]

    def GetDataQSAverage(self, axis: int):
        tempTS = self.ts.get_ts_between_times(0.0, 5.0, inclusive=True)
        qsAverage = self.Average(tempTS)
        return qsAverage[axis]
