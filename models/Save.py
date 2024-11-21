# -*- coding: utf-8 -*-
"""
Created on Mon May  9 17:34:13 2022

@author: Tom
"""
import pandas as pd
from models.MakeData import Data
from models import Loader


# Values for building excel sheet names in FormatSaveFile
P1 = "Phase 1 "
P2 = "Phase 2 "
AP = "Av-Arr "
ML = "G-D "
YP = "Axe Y"
YS = "Axe OPP Y"
XP = "Axe X"
XS = "Axe OPP X"
BS = "BS "
VA = 'Vit ABS '
VIT = 'Vitesse '
AV = 'Av'
ARR = 'Arr'
GAU = 'G'
DRT = 'D'
AXE_MVT = '- AXE MVT'
C_AXE_MVT = "- Contre AXE MVT"
ECART = 10
MAINT = 'Maintien EQ '


def AddToExistingSaveFile(dt: Data, path: str):
    isFirstColumnMA = dt.IsColumnMainAxis(1)
    indexColumn = getColumnIndexToWriteOn(dt)
    df = dt.ts.to_dataframe()
    firstcolumn = Loader.get_title_at(df, 1)
    secondcolumn = Loader.get_title_at(df, 2)
    indexPrint = indexColumn == 1

    if(indexPrint):
        indexColumn += -1

    # These writers parameters allow for adding to a sheet without writing over
    # Previous content, but do not allow for creation of new sheets
    writer = pd.ExcelWriter(path, engine='openpyxl',
                            if_sheet_exists='overlay', mode='a')

    i = 1
    while(i < 11):
        sheetName = getExpectedSheetName(dt, i)

        if(i % 2 == 1):
            if(isFirstColumnMA):
                df.to_excel(writer, sheet_name=sheetName, startcol=indexColumn,
                            startrow=1, columns=[firstcolumn],
                            index=indexPrint, index_label='Time (s)')
            else:
                df.to_excel(writer, sheet_name=sheetName, startcol=indexColumn,
                            startrow=1, columns=[secondcolumn],
                            index=indexPrint, index_label='Time (s)')
        else:
            if(isFirstColumnMA):
                df.to_excel(writer, sheet_name=sheetName, startcol=indexColumn,
                            startrow=1, columns=[secondcolumn],
                            index=indexPrint, index_label='Time (s)')
            else:
                df.to_excel(writer, sheet_name=sheetName, startcol=indexColumn,
                            startrow=1, columns=[firstcolumn],
                            index=indexPrint, index_label='Time (s)')
        if(i < 9):
            CalculateAndWriteDataToExcel(
                dt, path, columnNumber=indexColumn, isFirstColumn=indexPrint,
                writer=writer, pageNumber=i)
        else:
            CalculateAndWriteSpeedToExcel(
                dt, path, writer=writer, pageNumber=i)

        i += 1
    writer.close()


def CalculateAndWriteDataToExcel(dt: Data, path: str,
                                 columnNumber: int,
                                 isFirstColumn: bool,
                                 writer: pd.ExcelWriter,
                                 pageNumber: int):

    isFirstColumnMainAxis = dt.IsColumnMainAxis(1)
    df = dt.ts.to_dataframe()
    firstColumnTitle = Loader.get_title_at(df, 1)
    secondColumnTitle = Loader.get_title_at(df, 2)

    ts = dt.TSDataSubset(pageNumber)
    sheetName = getExpectedSheetName(dt, pageNumber)
    resArray = dt.SingleSaveDataFormat(pageNumber)
    row = 1  # Starting row for writing data
    isCurrentPageMainAxis = (pageNumber % 2 == 1)

    calculatingAtteinte = False

    for value in resArray:
        if(value == 0):
            label = 'Moyenne (cm)'
            temp = dt.Average(ts)
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    saveData = temp[0]
                    title = firstColumnTitle
                else:
                    saveData = temp[1]
                    title = secondColumnTitle
            else:
                if(isFirstColumnMainAxis):
                    saveData = temp[1]
                    title = secondColumnTitle
                else:
                    saveData = temp[0]
                    title = firstColumnTitle

        elif(value == 1):
            label = 'Écart Type (cm)'
            temp = dt.CalculateSTD(ts)
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    saveData = temp[0]
                else:
                    saveData = temp[1]
            else:
                if(isFirstColumnMainAxis):
                    saveData = temp[1]
                else:
                    saveData = temp[0]

        elif(value == 2):
            label = 'Étendue (cm)'
            temp = dt.CalculateExtent(ts)
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    saveData = temp[0]
                else:
                    saveData = temp[1]
            else:
                if(isFirstColumnMainAxis):
                    saveData = temp[1]
                else:
                    saveData = temp[0]

        elif(value == 3):
            label = 'Max pr QS (cm)'
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    qs = dt.GetDataQSAverage(0)
                    temp = dt.MaxByQS(qs, ts)
                    saveData = temp[0]
                else:
                    qs = dt.GetDataQSAverage(1)
                    temp = dt.MaxByQS(qs, ts)
                    saveData = temp[1]
            else:
                if(isFirstColumnMainAxis):
                    qs = dt.GetDataQSAverage(1)
                    temp = dt.MaxByQS(qs, ts)
                    saveData = temp[1]
                else:
                    qs = dt.GetDataQSAverage(0)
                    temp = dt.MaxByQS(qs, ts)
                    saveData = temp[0]

        elif(value == 4):
            label = 'N Max pr QS (cm)'
            temp = dt.MaxByQS(qs, ts)
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    if(dt.mainAxis):
                        saveData = temp[0] / dt.footLength
                    else:
                        saveData = temp[0] / dt.footWidth
                else:
                    if(dt.mainAxis):
                        saveData = temp[1] / dt.footLength
                    else:
                        saveData = temp[1] / dt.footWidth
            else:
                if(isFirstColumnMainAxis):
                    if(dt.mainAxis):
                        saveData = temp[1] / dt.footLength
                    else:
                        saveData = temp[1] / dt.footWidth
                else:
                    if(dt.mainAxis):
                        saveData = temp[0] / dt.footLength
                    else:
                        saveData = temp[0] / dt.footWidth

        elif(value == 5):
            label = 'Max - Moyenne (cm)'
            tempAverage = dt.Average(ts)
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    qs = dt.GetDataQSAverage(0)
                    tempMax = dt.MaxByQS(qs, ts)
                    tempAverageByQS = dt.AverageByQS(qs, tempAverage[0])
                    saveData = tempMax[0] - tempAverageByQS
                else:
                    qs = dt.GetDataQSAverage(1)
                    tempMax = dt.MaxByQS(qs, ts)
                    tempAverageByQS = dt.AverageByQS(qs, tempAverage[0])
                    saveData = tempMax[1] - tempAverageByQS
            else:
                if(isFirstColumnMainAxis):
                    qs = dt.GetDataQSAverage(1)
                    tempMax = dt.MaxByQS(qs, ts)
                    tempAverageByQS = dt.AverageByQS(qs, tempAverage[0])
                    saveData = tempMax[1] - tempAverageByQS
                else:
                    qs = dt.GetDataQSAverage(0)
                    tempMax = dt.MaxByQS(qs, ts)
                    tempAverageByQS = dt.AverageByQS(qs, tempAverage[0])
                    saveData = tempMax[0] - tempAverageByQS

        elif(value == 6):
            label = 'ABS Max pr QS (cm)'
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    qs = dt.GetDataQSAverage(0)
                    temp = dt.AbsoluteMaxByQS(qs, ts)
                    saveData = temp[0]
                else:
                    qs = dt.GetDataQSAverage(1)
                    temp = dt.AbsoluteMaxByQS(qs, ts)
                    saveData = temp[1]
            else:
                if(isFirstColumnMainAxis):
                    qs = dt.GetDataQSAverage(1)
                    temp = dt.AbsoluteMaxByQS(qs, ts)
                    saveData = temp[1]
                else:
                    qs = dt.GetDataQSAverage(0)
                    temp = dt.AbsoluteMaxByQS(qs, ts)
                    saveData = temp[0]

# Atteinte
        elif(value == 7):
            label = 'Atteinte :'
            saveData = ''
            ts = dt.TSDataSubset(pageNumber, atteinte=True)
            calculatingAtteinte = True

        elif(value == 8):
            label = 'Durée (s)'
            saveData = dt.Time(ts)

        elif(value == 9):
            label = 'Amplitude (cm)'
            temp = dt.Amplitude(ts)
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    saveData = temp[0]
                else:
                    saveData = temp[1]
            else:
                if(isFirstColumnMainAxis):
                    saveData = temp[1]
                else:
                    saveData = temp[0]

        elif(value == 10):
            label = 'Pente (cm/s)'
            temps = dt.Time(ts)
            pentes = dt.Pente(ts, temps=temps)
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    pente = pentes[0]
                else:
                    pente = pentes[1]
            else:
                if(isFirstColumnMainAxis):
                    pente = pentes[1]
                else:
                    pente = pentes[0]
            saveData = pente

# Vitesse
        elif(value == 11):
            label = 'Vitesse :'
            saveData = ''
            ts = dt.GetSpeedTS()
            ts = dt.TSDataSubset(pageNumber, ts=ts)

        elif(value == 12):
            label = 'Moyenne (cm/s)'
            temp = dt.Average(ts)
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    saveData = temp[0]
                else:
                    saveData = temp[1]
            else:
                if(isFirstColumnMainAxis):
                    saveData = temp[1]
                else:
                    saveData = temp[0]

        elif(value == 13):
            label = 'Écart-Type (cm/s)'
            temp = dt.CalculateSTD(ts)
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    saveData = temp[0]
                else:
                    saveData = temp[1]
            else:
                if(isFirstColumnMainAxis):
                    saveData = temp[1]
                else:
                    saveData = temp[0]

        elif(value == 14):
            label = 'Max (cm/s)'
            if(isCurrentPageMainAxis):
                if(isFirstColumnMainAxis):
                    temp = dt.MaxByQS(0, ts)
                    saveData = temp[0]
                else:
                    temp = dt.MaxByQS(0, ts)
                    saveData = temp[1]
            else:
                if(isFirstColumnMainAxis):
                    temp = dt.MaxByQS(0, ts)
                    saveData = temp[1]
                else:
                    temp = dt.MaxByQS(0, ts)
                    saveData = temp[0]

        elif(value == 15):
            label = "Vitesse de l'atteinte:"
            saveData = ''
            ts = dt.GetSpeedTS()
            ts = dt.TSDataSubset(pageNumber, ts=ts, atteinte=True)

        elif(value == 16):  # Only called on main axis page
            label = 'Maximum - Fin Atteinte (s)'
            ts = dt.GetGroupedTS()
            saveData = dt.TimeAttMax(ts)

        elif (value == 17):  # Must be called after 16, always on main page
            label = 'Maximum - Fin Atteinte (cm)'
            temp = dt.DistMaxAtt(ts)
            if(isFirstColumnMainAxis):
                saveData = temp[0]
            else:
                saveData = temp[1]
        else:
            raise Exception('Unhandled value in the save table')

        df = pd.DataFrame([saveData], index=[label], columns=[title])
        df.to_excel(writer, sheet_name=sheetName, startcol=columnNumber+ECART,
                    startrow=row, index=isFirstColumn, header=(row == 1))
        if(row == 1):  # To account for title row
            row += 1
        row += 1

        if(str(saveData) != ''):
            if(calculatingAtteinte == False):
                dt.savelist[pageNumber - 1].append(saveData)
            else:
                # +6 to move from P1 page number to atteinte page number in groupsavefile
                dt.savelist[pageNumber - 1 + 6].append(saveData)


# Input: Data, sheet number from 1 to 10
# Output: Corresponding sheet name
def getExpectedSheetName(dt: Data, sheetNumber: int):

    if sheetNumber < 3:
        sheetName = P2
    elif sheetNumber < 5:
        sheetName = P1
    elif sheetNumber < 7:
        sheetName = BS
    elif sheetNumber < 9:
        sheetName = MAINT
    else:
        sheetName = VIT

    if (sheetNumber % 2 == 0):
        sheetName += C_AXE_MVT
    elif(sheetNumber % 2 == 1):
        sheetName += AXE_MVT

    return sheetName


def getColumnIndexToWriteOn(dt: Data):
    if dt.mainAxis:  # Axis Av-Arr
        if not dt.direction:  # if Av
            if dt.eyesOpen:
                return 1
            else:
                return 2
        else:  # if Arr
            if dt.eyesOpen:
                return 3
            else:
                return 4
    else:  # Axis G-D
        if not dt.direction:  # if G
            if dt.eyesOpen:
                return 5
            else:
                return 6
        else:  # if D
            if dt.eyesOpen:
                return 7
            else:
                return 8


# Allows for the creation of a formated excel document
# with the good number of sheets and names (10 sheets)
def FormatSaveFile(dt: Data, path: str):
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    pageNum = 1
    while (pageNum < 11):
        sheet = getExpectedSheetName(dt, pageNum)
        writer.write_cells(cells='', sheet_name=sheet)

        df = pd.DataFrame(columns=[AP, '', '', '', ML])
        df.to_excel(writer, sheet_name=sheet, startcol=ECART + 1,
                    startrow=0, index=False, header=True)
        if(pageNum > 8):
            # Vitesse
            FormatSpeedSheets(dt, path, writer, sheet=sheet,
                              pageNumber=pageNum)
        pageNum += 1

    writer.close()


def FormatSpeedSheets(dt: Data, path: str, writer: pd.ExcelWriter, sheet: str, pageNumber: int):
    df = pd.DataFrame(
        columns=[VA + AV, '', VA + ARR, '', VA + GAU, '', VA + DRT, ''])

    df.to_excel(writer, sheet_name=sheet, startcol=ECART,
                startrow=0, index=False, header=True)


def CalculateAndWriteSpeedToExcel(dt: Data, path: str,
                                  writer: pd.ExcelWriter, pageNumber: int):
    speedTS = dt.GetSpeedTS()
    df = speedTS.to_dataframe()
    isFirstColumnMA = dt.IsColumnMainAxis(1)
    firstcolumn = Loader.get_title_at(df, 1)
    secondcolumn = Loader.get_title_at(df, 2)
    indexColumn = getColumnIndexToWriteOn(dt)

    sheetName = getExpectedSheetName(dt, pageNumber)

    if(pageNumber == 9):
        if(isFirstColumnMA):
            df.to_excel(writer, sheet_name=sheetName, startcol=indexColumn + ECART - 1,
                        startrow=1, columns=[firstcolumn],
                        index=False)
        else:
            df.to_excel(writer, sheet_name=sheetName, startcol=indexColumn + ECART - 1,
                        startrow=1, columns=[secondcolumn],
                        index=False)
    else:
        if(isFirstColumnMA):
            df.to_excel(writer, sheet_name=sheetName, startcol=indexColumn + ECART - 1,
                        startrow=1, columns=[secondcolumn],
                        index=False)
        else:
            df.to_excel(writer, sheet_name=sheetName, startcol=indexColumn + ECART - 1,
                        startrow=1, columns=[firstcolumn],
                        index=False)
