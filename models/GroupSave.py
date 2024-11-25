# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:06:03 2022

@author: Tom
"""
from models.Save import AP, ML, ECART, P2, P1, BS, C_AXE_MVT, AXE_MVT, getColumnIndexToWriteOn
import pandas as pd
from models.MakeData import Data

ATT = 'Atteinte '
NUMBER_OF_PAGES = 10
# Allows for the creation of a formated excel document
# with the good number of sheets and names (8 sheets)


def FormatGroupSaveFile(dt: Data, path: str):
    writer = pd.ExcelWriter(path, engine='xlsxwriter')

    pageNum = 1
    while (pageNum <= NUMBER_OF_PAGES):
        columnToWrite = 1
        sheet = getExpectedGroupSheetName(dt, pageNum)
#        writer.write_cells(cells='', sheet_name=sheet)

        dataFormat = dt.GroupSaveDataFormat(pageNum)
        size = len(dataFormat)
        if(dataFormat.__contains__(7)):
            size -= 1
        if(dataFormat.__contains__(11)):
            size -= 1
        if(dataFormat.__contains__(15)):
            size -= 1

        for x in dataFormat:
            if(x == 7 or x == 11 or x == 15):
                continue

            df1 = pd.DataFrame(columns=[dt.DataListToText(x)])
            df1.to_excel(writer, sheet_name=sheet, startcol=columnToWrite,
                         startrow=0, index=False, header=True)

            df = pd.DataFrame(columns=['av yo', 'av yff', 'arr yo',
                              'arr yff', 'g yo', 'g yff', 'd yo', 'd yff'])
            df.to_excel(writer, sheet_name=sheet, startcol=columnToWrite,
                        startrow=1, index=False, header=True)
            columnToWrite += ECART

        pageNum += 1

    writer.close()


# Input: Data, sheet number from 1 to NUMBER_OF_PAGES
# Output: Corresponding sheet name
def getExpectedGroupSheetName(dt: Data, sheetNumber: int):

    if sheetNumber < 3:
        sheetName = P2
    elif sheetNumber < 5:
        sheetName = P1
    elif sheetNumber < 7:
        sheetName = BS
    elif sheetNumber < 9:
        sheetName = 'Maintien EQ '
    else:
        sheetName = ATT

    if (sheetNumber % 2 == 0):
        sheetName += C_AXE_MVT
    elif(sheetNumber % 2 == 1):
        sheetName += AXE_MVT

    return sheetName


def SaveToExistingGroup(data: Data, groupDataPath: str, rowToWrite: int, participant: str):
    writer = pd.ExcelWriter(groupDataPath, engine='openpyxl',
                            if_sheet_exists='overlay', mode='a')

    groupDataList = data.savelist
    columnStart = getColumnIndexToWriteOn(data)

    i = 0
    while i < len(groupDataList):
        sheetName = getExpectedGroupSheetName(data, i + 1)
        column = columnStart
        j = 0
        while j < len(groupDataList[i]):
            savelist = groupDataList[i]
            df = pd.DataFrame([savelist[j]], index=[participant])
            if(columnStart == 1):
                df.to_excel(writer, sheet_name=sheetName, startcol=column - 1,
                            startrow=rowToWrite - 1, index=True, header=False)
            else:
                df.to_excel(writer, sheet_name=sheetName, startcol=column,
                            startrow=rowToWrite - 1, index=False, header=False)

            column += ECART
            j += 1

        i += 1

    writer.close()
