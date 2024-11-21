# -*- coding: utf-8 -*-
"""
Created on Wed May 11 14:02:39 2022

@author: Tom
"""

from models.MakeData import CreateTS, Data
from models.Save import AddToExistingSaveFile, FormatSaveFile
from models.GroupSave import FormatGroupSaveFile, SaveToExistingGroup

DISTANCE = 5.00
BS_START_NAME = 'Debut du backshift'
BS_PEAK_NAME = 'Peak du BS'
PHASE_1_NAME = 'Phase 1'
PHASE_2_NAME = 'Phase 2'
PHASE_1_2_TRANSITION_NAME = 'Phase 1 - Phase 2'
MAX_ATT = 'Maximum'


def initialiseData(path: str):
    ts = CreateTS(path)
    dt = Data(ts)
    return dt


def addBSPhaseStart(dt: Data, time: float):
    try:
        dt.ts.remove_event(BS_START_NAME, in_place=True)
    except:
        pass
    dt.AddEvent(BS_START_NAME, time)


def addBSPhasePeak(dt: Data, time: float):
    try:
        dt.ts.remove_event(BS_PEAK_NAME, in_place=True)
    except:
        pass
    dt.AddEvent(BS_PEAK_NAME, time)


def addPhase1(dt: Data, time: float):
    try:
        dt.ts.remove_event(PHASE_1_NAME, in_place=True)
    except:
        pass
    dt.AddEvent(PHASE_1_NAME, time)


def addMaxAtteinte(dt: Data, time: float):
    try:
        dt.ts.remove_event(MAX_ATT, in_place=True)
    except:
        pass
    dt.AddEvent(MAX_ATT, time)


def addPhase2(dt: Data, mod: float):
    try:    
        dt.ts.remove_event(PHASE_2_NAME, in_place=True)
    except:
        pass
    try:    
        dt.ts.remove_event(PHASE_1_2_TRANSITION_NAME, in_place=True)
    except:
        pass
    dt.AddEvent(PHASE_2_NAME, 15.0 + mod)
    dt.AddEvent(PHASE_1_2_TRANSITION_NAME, 10.0 + mod)


def SaveToNewDocument(data: Data, singleDataPath: str):
    addPhase2(data, 0)
    FormatSaveFile(data, singleDataPath)
    AddToExistingSaveFile(data, path=singleDataPath)


def SaveToExistingDocument(data: Data, singleDataPath: str):
    addPhase2(data, 0)
    AddToExistingSaveFile(data, path=singleDataPath)


def NewGroupDocument(data: Data, groupDataPath: str):
    FormatGroupSaveFile(data, path=groupDataPath)


def SaveToExistingGroupDocument(data: Data, groupDataPath: str, rowToWrite: int, participant: str):
    SaveToExistingGroup(data=data, groupDataPath=groupDataPath,
                        rowToWrite=rowToWrite, participant=participant)
