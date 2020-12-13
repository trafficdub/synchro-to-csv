#################################################
#Synchro Intersection Summary Tool              #
#Created By Yuzhu Huang @ Jacobs                #
#August 30, 2019                                #
#################################################

#from tkinter import *     # Imports tkinter and all subdirectory files.
from tkinter import Tk
from tkinter import messagebox
from tkinter import filedialog
import csv
import os
import numpy as np
import pandas as pd

REPORT_TYPE_DICT = {'Sig6th': 'HCM 6th Signalized Intersection Summary', \
                    'Awsc6th': 'HCM 6th AWSC', \
                    'Twsc6th': 'HCM 6th TWSC', \
                    'Sig2010': 'HCM 2010 Signalized Intersection Summary', \
                    'Awsc2010': 'HCM 2010 AWSC', \
                    'Twsc2010': 'HCM 2010 TWSC', \
                    'Sig2000': 'HCM Signalized Intersection Capacity Analysis', \
                    'Unsig2000': 'HCM Unsignalized Intersection Capacity Analysis', \
                    'LaneVolTim': 'Lanes, Volumes, Timings'}

tk = Tk()
tk.withdraw()     # hides tkinter window

NEW_TYPE = "2010"
if messagebox.askquestion(title= "Warning", message = "This tool will summarize intersection HCM 2010 Results from Synchro, Continue?")=="no":
	NEW_TYPE = "6th"
	if messagebox.askquestion(title= "Warning", message = "This tool will summarize intersection HCM 6th Edition Results from Synchro, Continue?")=="no":
		sys.exit()



############ Open .txt file and create .CSV file ###############
if NEW_TYPE == "2010":
	file_path = filedialog.askopenfilename(title="Open HCM 2010 Signalized Text File",
										   filetypes=[("summary",".txt"),
													  ("All files",".*")])

	file_path_new_awsc = filedialog.askopenfilename(title="Open HCM 2010 AWSC Text File",
										   filetypes=[("summary",".txt"),
													  ("All files",".*")])

	file_path_new_twsc = filedialog.askopenfilename(title="Open HCM 2010 TWSC Text File",
									   filetypes=[("summary",".txt"),
												  ("All files",".*")])
    
	file_path_2000 = filedialog.askopenfilename(title="Open HCM 2000 Signalized Text File",
										   filetypes=[("summary",".txt"),
													  ("All files",".*")])

	file_path_unSig2000 = filedialog.askopenfilename(title="Open HCM 2000 Unsignalized Text File",
										   filetypes=[("summary",".txt"),
													  ("All files",".*")])
else:
	file_path = filedialog.askopenfilename(title="Open HCM 6th Signalized Text File",
										   filetypes=[("summary",".txt"),
													  ("All files",".*")])

	file_path_new_awsc = filedialog.askopenfilename(title="Open HCM 6th AWSC Text File",
										   filetypes=[("summary",".txt"),
													  ("All files",".*")])

	file_path_new_twsc = filedialog.askopenfilename(title="Open HCM 6th TWSC Text File",
									   filetypes=[("summary",".txt"),
												  ("All files",".*")])

	file_path_2000 = filedialog.askopenfilename(title="Open HCM 2000 Signalized Text File",
										   filetypes=[("summary",".txt"),
													  ("All files",".*")])

	file_path_unSig2000 = filedialog.askopenfilename(title="Open HCM 2000 Unsignalized Text File",
										   filetypes=[("summary",".txt"),
													  ("All files",".*")])

def openTxtFile(file_Name):
    with open(file_Name, "r") as f:
        file_to_list = list(csv.reader(f, delimiter="\t"))
    df = pd.DataFrame(file_to_list)
    return df

# Find Location of the first, second and last row for each intersection
### !!Consider try catch to check length of arrays
def findFeatRow(df, reportType):
    FirstRowLoc = df.loc[df.iloc[:,0] == reportType].index.values
    IntxRowLoc = FirstRowLoc + 1
    LastRowLoc = df.loc[df.iloc[:,1].str.contains("Page") == True].index.values
    IntxList = df.loc[IntxRowLoc, 0].str.split(": ", n = 1, expand = True)
    tempIntx = pd.DataFrame(columns=['ID', 'Location'])
    IntxList.reset_index(drop = True, inplace = True)
    tempIntx['ID'] = IntxList.loc[:,0]
    tempIntx['Location'] = IntxList.loc[:,1]
    featRowLoc = pd.DataFrame({'First': FirstRowLoc, 'Intx': IntxRowLoc, \
                               'Last': LastRowLoc, 'ID': tempIntx['ID'], 'Location': tempIntx['Location']})
    return featRowLoc

from bisect import bisect_left
def findMatch(intxRowList, x):
    return intxRowList[bisect_left(intxRowList, x) - 1]

def getTempResult(df, featRow, header, measure):
    temp = pd.DataFrame()
    idList = pd.DataFrame()
    measureList = pd.DataFrame()
    if measure == 'HCM 2000 Level of Service':
        measureLookup = 'HCM 2000 Control Delay'
    else:
        measureLookup = measure
    tempRowLoc = df.loc[df.iloc[:,0].str.contains(fr'\b^{measureLookup}\s*\b') == True].index.values
    intxRowList = featRow['Intx'].values
    tempLowerMatch = np.array([findMatch(intxRowList, i) for i in tempRowLoc])
    idList = featRow.loc[featRow['Intx'].isin(tempLowerMatch), 'ID']
    idList.reset_index(drop = True, inplace = True)
    if measure == 'HCM 2000 Level of Service':
        measureList = df.loc[tempRowLoc,10]
    elif measure == 'HCM 2000 Control Delay':
        measureList = df.loc[tempRowLoc,4]
    else:
        measureList1 = df.loc[tempRowLoc,:].replace(r'^\s*$', np.nan, regex=True)
        measureList = measureList1.ffill(axis = 1).iloc[:, -1]
    
    measureList.reset_index(drop = True, inplace = True)
    temp['ID'] = idList
    temp[header] = measureList
    return temp

def getSubRowFeat(df, firstRowLookup, lastRowLookup, intxRowList):
    tempFirstRowLoc = df.loc[df.iloc[:,0].str.contains(fr'\b^{firstRowLookup}\s*\b') == True].index.values
    tempFirstLowerMatch = np.array([findMatch(intxRowList, i) for i in tempFirstRowLoc])
    tempLastRowLoc = df.loc[df.iloc[:,0].str.contains(fr'\b^{lastRowLookup}\s*\b') == True].index.values
    tempLastLowerMatch = np.array([findMatch(intxRowList, i) for i in tempLastRowLoc])

    tempList = {'IntxFirst': tempFirstLowerMatch, 'IntxLast':  tempLastLowerMatch, \
                'firstRow': tempFirstRowLoc, 'lastRow': tempLastRowLoc}
    return tempList

def transposeDf(df, firstRow, lastRow):
    tempDf = df.loc[firstRow: lastRow, 1: ]
    temp_index = df.loc[firstRow: lastRow, 0]
    tempDf.index = temp_index
    tempDf_trans = tempDf.transpose()
    tempDf_trans.reset_index(drop = True, inplace = True)
    return tempDf_trans

def get6th2010Twsc(df, repType):
    if repType == 'HCM 6th':
        report_Type = REPORT_TYPE_DICT['Twsc6th']
    elif repType == 'HCM 2010':
        report_Type = REPORT_TYPE_DICT['Twsc2010']
    featRow = findFeatRow(df, report_Type)
    intxRowList = featRow['Intx'].values
    idList = featRow['ID'].values
    locList = featRow['Location'].values

    stopLookup = getSubRowFeat(df, "Movement", "Mvmt Flow", intxRowList)
    resultLookup = getSubRowFeat(df, "Minor Lane/Major Mvmt", "HCM 95th", intxRowList)

    worstSummary = pd.DataFrame(columns = ['ID', 'Delay', 'LOS', 'Location'])
    
    for i in range(0, len(intxRowList)):
        stop_trans = transposeDf(df, stopLookup['firstRow'][i], stopLookup['lastRow'][i])
        result_trans = transposeDf(df, resultLookup['firstRow'][i], resultLookup['lastRow'][i])
        signControlHeader = stop_trans.filter(regex = 'Sign Control\s*').columns.values[0]
        mvmtHeader = stop_trans.filter(regex = 'Movement\s*').columns.values[0]
        minMajHeader = result_trans.filter(regex = 'Minor Lane/Major Mvmt\s*').columns.values[0]
        vcHeader = result_trans.filter(regex = 'HCM Lane V/C Ratio\s*').columns.values[0]
        delayHeader = result_trans.filter(regex = 'HCM Control Delay\s*').columns.values[0]
        losHeader = result_trans.filter(regex = 'HCM Lane LOS\s*').columns.values[0]

        stopMvmt = stop_trans.loc[stop_trans[signControlHeader] == 'Stop', mvmtHeader]
        
        result_trans[delayHeader].astype(str).apply(lambda x: x.replace('$', ''))
        resultStopMvmt = result_trans.loc[result_trans[minMajHeader].str[:2].isin(stopMvmt.str[:2])]
        resultWorstMvmt = resultStopMvmt.sort_values(delayHeader, ascending = False).reset_index(drop = True).loc[0, :]
        worstMvmtMeasure = {'delay': resultWorstMvmt[delayHeader], 'los': resultWorstMvmt[losHeader]}
        worstSummary.loc[i, 'ID'] = idList[i]
        worstSummary.loc[i, 'Delay'] = resultWorstMvmt[delayHeader]
        worstSummary.loc[i, 'LOS'] = resultWorstMvmt[losHeader]
        worstSummary.loc[i, 'Location'] = locList[i]

    if repType == 'HCM 6th':
        worstSummary['Report'] = "HCM 6th TWSC"
    elif repType == 'HCM 2010':
        worstSummary['Report'] = "HCM 2010 TWSC"
    return worstSummary
    
def get2000Twsc(df):
    report_Type = REPORT_TYPE_DICT['Unsig2000']
    featRow = findFeatRow(df, report_Type)
    intxRowList = featRow['Intx'].values
    allTypeLookup = getSubRowFeat(df, "Movement", "Hourly flow rate", intxRowList)
    stopLookup = getSubRowFeat(df, "Movement", "Sign Control", intxRowList)
    stop_First = dict((k, stopLookup[k]) for k in ('IntxFirst', 'firstRow'))
    stop_Last = dict((k, stopLookup[k]) for k in ('IntxLast', 'lastRow'))
    stopLookup_dfFirst = pd.DataFrame(stop_First)
    stopLookup_dfLast = pd.DataFrame(stop_Last)

    featRow_new = pd.merge(stopLookup_dfLast, featRow, how = 'inner', left_on = 'IntxLast', right_on = 'Intx')

    idList = featRow_new['ID'].values
    locList = featRow_new['Location'].values
    test = stopLookup_dfFirst.loc[stopLookup_dfFirst.IntxFirst.isin(stopLookup_dfLast.IntxLast)].reset_index(drop = True)
    stopLookup['IntxFirst'] = test.loc[:, 'IntxFirst'].values
    stopLookup['firstRow'] = test.loc[:, 'firstRow'].values

    resultLookup = getSubRowFeat(df, "Direction, Lane", "Approach LOS", intxRowList)

    worstSummary = pd.DataFrame(columns = ['ID', 'Delay', 'LOS', 'Location'])
    sumCount = 0
    for i in range(0, len(stopLookup['IntxLast'])):
        stop_trans = transposeDf(df, stopLookup['firstRow'][i], stopLookup['lastRow'][i])
        result_trans = transposeDf(df, resultLookup['firstRow'][i], resultLookup['lastRow'][i])
        signControlHeader = stop_trans.filter(regex = 'Sign Control\s*').columns.values[0]
        searchfor = ['Free', 'Yield']
        mustHas = ['Stop']
        stopTypes = stop_trans.loc[:, signControlHeader].unique()
        if any(x in searchfor for x in stopTypes):
            if any(x in mustHas for x in stopTypes):
                print('has')
                print(stopTypes)
                mvmtHeader = stop_trans.filter(regex = 'Movement\s*').columns.values[0]
                volumeHeader = stop_trans.filter(regex = 'Traffic Volume\s*').columns.values[0]

                minMajHeader = result_trans.filter(regex = 'Direction, Lane\s*').columns.values[0]
                vcHeader = result_trans.filter(regex = 'Volume to Capacity\s*').columns.values[0]
                delayHeader = result_trans.filter(regex = 'Control Delay\s*').columns.values[0]
                losHeader = result_trans.filter(regex = 'Lane LOS\s*').columns.values[0]]

                stopMvmt = stop_trans.loc[stop_trans[signControlHeader] == 'Stop', mvmtHeader]
                print(stopMvmt)
                stop_trans_stopMvmt = stop_trans.loc[stop_trans[mvmtHeader].str[:2].isin(stopMvmt.str[:2])]
                print(stop_trans_stopMvmt)
                sumStopVol = pd.to_numeric(stop_trans_stopMvmt.loc[:, volumeHeader]).replace(np.nan, 0, regex = True).values.sum()

                print(sumStopVol)
                if  sumStopVol > 0:
                    result_trans[delayHeader].astype(str).apply(lambda x: x.replace('$', ''))
                    resultStopMvmt = result_trans.loc[result_trans[minMajHeader].str[:2].isin(stopMvmt.str[:2])]
                    print(resultStopMvmt)
                    resultWorstMvmt = resultStopMvmt.sort_values(delayHeader, ascending = False).reset_index(drop = True).loc[0, :]
                    print(resultWorstMvmt)
                    worstMvmtMeasure = {'delay': resultWorstMvmt[delayHeader], 'los': resultWorstMvmt[losHeader]}
                    worstSummary.loc[sumCount, 'ID'] = idList[i]
                    worstSummary.loc[sumCount, 'Delay'] = resultWorstMvmt[delayHeader]
                    worstSummary.loc[sumCount, 'LOS'] = resultWorstMvmt[losHeader]
                    worstSummary.loc[sumCount, 'Location'] = locList[i]
                    worstSummary['Report'] = "HCM 2000 TWSC"
                    sumCount = sumCount + 1
            print('does not')
    return worstSummary

def get6thSig(df):
    report_Type = REPORT_TYPE_DICT['Sig6th']
    featRow = findFeatRow(df, report_Type)
    delayName = 'Delay'
    losName = 'LOS'
    measureDict = {delayName: 'HCM 6th Ctrl Delay', \
                   losName: 'HCM 6th LOS'}
    delayTemp = getTempResult(df, featRow, delayName, measureDict[delayName])
    losTemp = getTempResult(df, featRow, losName, measureDict[losName])
    measureTemp = pd.merge(delayTemp, losTemp, on = 'ID')
    resultTemp = pd.merge(measureTemp, featRow.loc[:,'ID':'Location'], on = 'ID')
    resultTemp['IntxV_c'] = np.nan
    resultTemp['Report'] = "HCM 6th Signalized"
    return resultTemp

def get6thAwsc(df):
    report_Type = REPORT_TYPE_DICT['Awsc6th']
    featRow = findFeatRow(df, report_Type)
    delayName = 'Delay'
    losName = 'LOS'
    measureDict = {delayName: 'Intersection Delay, s/veh', \
                   losName: 'Intersection LOS'}
    delayTemp = getTempResult(df, featRow, delayName, measureDict[delayName])
    losTemp = getTempResult(df, featRow, losName, measureDict[losName])
    measureTemp = pd.merge(delayTemp, losTemp, on = 'ID')
    resultTemp = pd.merge(measureTemp, featRow.loc[:,'ID':'Location'], on = 'ID')
    resultTemp['Report'] = "HCM 6th AWSC"
    return resultTemp

def get2010Sig(df):
    report_Type = REPORT_TYPE_DICT['Sig2010']
    featRow = findFeatRow(df, report_Type)
    delayName = 'Delay'
    losName = 'LOS'
    measureDict = {delayName: 'HCM 2010 Ctrl Delay', \
                   losName: 'HCM 2010 LOS'}
    delayTemp = getTempResult(df, featRow, delayName, measureDict[delayName])
    losTemp = getTempResult(df, featRow, losName, measureDict[losName])
    measureTemp = pd.merge(delayTemp, losTemp, on = 'ID')
    resultTemp = pd.merge(measureTemp, featRow.loc[:,'ID':'Location'], on = 'ID')
    resultTemp['IntxV_c'] = np.nan
    resultTemp['Report'] = "HCM 2010 Signalized"
    return resultTemp

def get2010Awsc(df):
    report_Type = REPORT_TYPE_DICT['Awsc2010']
    featRow = findFeatRow(df, report_Type)
    delayName = 'Delay'
    losName = 'LOS'
    measureDict = {delayName: 'Intersection Delay, s/veh', \
                   losName: 'Intersection LOS'}
    delayTemp = getTempResult(df, featRow, delayName, measureDict[delayName])
    losTemp = getTempResult(df, featRow, losName, measureDict[losName])
    measureTemp = pd.merge(delayTemp, losTemp, on = 'ID')
    resultTemp = pd.merge(measureTemp, featRow.loc[:,'ID':'Location'], on = 'ID')
    resultTemp['Report'] = "HCM 2010 AWSC"
    return resultTemp

def get2000Sig(df):
    report_Type = REPORT_TYPE_DICT['Sig2000']
    featRow = findFeatRow(df, report_Type)
    delayName = 'Delay'
    losName = 'LOS'
    vcName = 'IntxV_c'
    measureDict = {delayName: 'HCM 2000 Control Delay', \
                   losName: 'HCM 2000 Level of Service', \
                   vcName: 'HCM 2000 Volume to Capacity ratio'}
    vcTemp = getTempResult(df, featRow, vcName, measureDict[vcName])
    delayTemp = getTempResult(df, featRow, delayName, measureDict[delayName])
    losTemp = getTempResult(df, featRow, losName, measureDict[losName])
    measureTemp = pd.merge(delayTemp, losTemp, on = 'ID')
    measureTemp2 = pd.merge(measureTemp, vcTemp, on = 'ID')
    resultTemp = pd.merge(measureTemp2, featRow.loc[:,'ID':'Location'], on = 'ID')
    resultTemp['Report'] = "HCM 2000 Signalized"
    return resultTemp

def get2000Awsc(df):
    report_Type = REPORT_TYPE_DICT['Unsig2000']
    featRow = findFeatRow(df, report_Type)
    delayName = 'Delay'
    losName = 'LOS'
    measureDict = {delayName: 'Delay', \
                   losName: 'Level of Service'}
    delayTemp = getTempResult(df, featRow, delayName, measureDict[delayName])
    losTemp = getTempResult(df, featRow, losName, measureDict[losName])
    measureTemp = pd.merge(delayTemp, losTemp, on = 'ID')
    resultTemp = pd.merge(measureTemp, featRow.loc[:,'ID':'Location'], on = 'ID')
    resultTemp['Report'] = "HCM 2000 AWSC"
    return resultTemp

def getHcmResult(file_Name, hcm_Type):
    df = openTxtFile(file_Name)
    if hcm_Type == 1:
        return get6thSig(df)
    elif hcm_Type == 2:
        return get6thAwsc(df)
    elif hcm_Type == 3:
        return get6th2010Twsc(df, 'HCM 6th')
    elif hcm_Type == 4:
        return get2010Sig(df)
    elif hcm_Type == 5:
        return get2010Awsc(df)
    elif hcm_Type == 6:
        return get6th2010Twsc(df, 'HCM 2010')
    elif hcm_Type == 7:
        return get2000Sig(df)
    elif hcm_Type == 8:
        return get2000Awsc(df)
    elif hcm_Type == 9:
        return get2000Twsc(df)
    elif hcm_Type == 10:
        return 'check'

if NEW_TYPE == "2010":
	sigNewerHcmResult = getHcmResult(file_path, 4)
	awscNewerHcmResult = getHcmResult(file_path_new_awsc, 5)
	twscNewerHcmResult = getHcmResult(file_path_new_twsc, 6)
elif NEW_TYPE == "6th":
	sigNewerHcmResult = getHcmResult(file_path, 1)
	awscNewerHcmResult = getHcmResult(file_path_new_awsc, 2)
	twscNewerHcmResult = getHcmResult(file_path_new_twsc, 3)

sig2000HcmResult = getHcmResult(file_path_2000, 7)
awsc2000HcmResult = getHcmResult(file_path_unSig2000, 8)
twsc2000HcmResult = getHcmResult(file_path_unSig2000, 9)


sigCombined_print = sig2000HcmResult.loc[:, :]
sigCombined_print.loc[sigCombined_print.ID.isin(sigNewerHcmResult.ID), \
                          ['Delay', 'LOS', 'Report']] = sigNewerHcmResult[['Delay', \
                                                                                      'LOS', 'Report']].values

if len(awsc2000HcmResult['ID']) >= len(awscNewerHcmResult['ID']):
    awscCombined_temp1 = awsc2000HcmResult.loc[:, :]
    awscCombined_temp1.loc[awsc2000HcmResult.ID.isin(awscNewerHcmResult.ID), \
                              ['Delay', 'LOS', 'Report']] = awscNewerHcmResult[['Delay', 'LOS', 'Report']].values
    awscCombined_temp = awscNewerHcmResult.loc[~awscNewerHcmResult.ID.isin(awscCombined_temp1.ID),:].append(awscCombined_temp1, ignore_index = True, sort = True)
else:
    awscCombined_temp = awsc2000HcmResult.loc[~awsc2000HcmResult.ID.isin(awscNewerHcmResult.ID),:].append(awscNewerHcmResult, ignore_index = True, sort = True)

if len(twsc2000HcmResult['ID']) >= len(twscNewerHcmResult['ID']):
    twscCombined_temp1 = twsc2000HcmResult.loc[:, :]
    twscCombined_temp1.loc[twsc2000HcmResult.ID.isin(twscNewerHcmResult.ID), \
                              ['Delay', 'LOS', 'Report']] = twscNewerHcmResult[['Delay', 'LOS', 'Report']].values
    twscCombined_temp = twscNewerHcmResult.loc[~twscNewerHcmResult.ID.isin(twscCombined_temp1.ID),:].append(twscCombined_temp1, ignore_index = True, sort = True)
else:
    twscCombined_temp = twsc2000HcmResult.loc[~twsc2000HcmResult.ID.isin(twscNewerHcmResult.ID),:].append(twscNewerHcmResult, ignore_index = True, sort = True)

unsigCombined_print = awscCombined_temp.append(twscCombined_temp, ignore_index = True, sort = True)
print(unsigCombined_print)

all_combined = sigCombined_print.append(unsigCombined_print, ignore_index = True, sort = True)
all_combined['ID'] = pd.to_numeric(all_combined['ID'])
all_print = all_combined.sort_values('ID', ascending = True).reset_index(drop = True).loc[:, :]

folder_path = os.path.dirname(file_path)
all_print.to_csv(folder_path + r'\report.csv')
