import pyautogui as pa
import time
import pandas as pd
from openpyxl import load_workbook
import datetime
import logging
from types import SimpleNamespace
import clipboard as cb
import pyodbc
import subprocess # to call notepad.exe

import config  # import global variables
import mylib
import sqlserver as sql

#De reload module: python version >= 3.4
#import importlib
#importlib.reload(module)

#Log DB:
DBfile = 'C:/Data/SkdChg1A.accdb'

#File access tren may local va SQL Server tren may chu de luu du lieu SC:
access_cursor = access_conn = 0
sql_cursor = sql_conn = 0


def wait_until_window_closed(wind, timeout, period=0.2):
    # wind la 1 tuple or list of tuple
    # Wait max timeout seconds, or wind close:
    
    if type(wind) == tuple: # truyen 1 wind la 1 tuple
        wind_arr = [wind] # convert to list
    else:
        wind_arr = wind

    must_end = time.time() + timeout
    while time.time() < must_end and not config.bStop:
        time.sleep(period)
        for window in wind_arr:
            if pa.locateOnScreen(window[0], grayscale=True, confidence=.9) is None:
                return True

    wind_title = ' or '.join([w[3] for w in wind_arr])    
    raise Exception(f'Error: time out while waiting window {wind_title} closed')
    
    
def wait_until_window_open(wind, timeout, period=1):
    # wind la 1 tuple or list of tuple
    #  Wait max timeout seconds, or wind open:
    
    if type(wind) == tuple: # truyen 1 wind la 1 tuple
        wind_arr = [wind] # convert to list
    else:
        wind_arr = wind
        
    must_end = time.time() + timeout
    #print('Waiting for window open: ', wind)
    while time.time() < must_end and not config.bStop:
        time.sleep(period)        
        for window in wind_arr:
            box = pa.locateOnScreen(window[0], grayscale=True, confidence=.8)
            if box is not None: # 1 trong cac input windows open
                time.sleep(0.1) # wait more 0.1 second so window really open
                return box # window position
                
    wind_title = ' or '.join([w[3] for w in wind_arr])
    logStr = f'Error: timeout while waiting windows {wind_title} open!' 
    raise Exception(logStr) # window NOT open


def wait_image_disappear(image_name, timeout, period=0.2):
    #Input: image_name
    #Output: wait until image_name disappear on screen, or timeout
    
    mustend = time.time() + timeout
    while time.time() < mustend and not config.bStop:
        time.sleep(period)

        if pa.locateOnScreen(image_name, grayscale=True, confidence=.9) is None:
            time.sleep(period)        
            return True

    raise Exception('Error: timeout while waiting image ' + image_name + ' disappear!')
    

def close_win(win):
    win_pos = pa.locateOnScreen(win[0], grayscale=True, confidence=.9)
    if win_pos is None:
        raise Exception('Cannot find window ' + win[3])
    else:
        pa.click(win_pos)        
        time.sleep(0.1)
        pa.press('esc')
        wait_until_window_closed(win, 10)
            
    
def readExcelFile(fullFileName, column_type=None):
    #xls = pd.ExcelFile(fullFileName)
    #df = xls.parse(xls.sheet_names[0])
    #print('fullFileName = ', fullFileName)
    df = pd.read_excel(fullFileName, sheet_name=0, header=0, dtype=column_type) #, index_col=0)
    #Need to make sure pd close file after opening
    return df


def read_acv_file(bStaging):
    #Input: bStaging
    #Output: df_acv
    
    if bStaging:
        ACV_FileName = "ACV_Staging.xlsx"
    else:
        ACV_FileName = "ACV.xlsx"

    acv_type = {'AcvCode': str, 'SaleCode': str, 'EquipmentType': str}
    df_acv = readExcelFile(ACV_FileName, column_type= acv_type)
    return df_acv


def readExcel_KHDB(fullFileName):
    logStr = 'readExcel_KHDB'
    print(logStr)
    logging.warning(logStr)
        
    dtype = {'FLT NBR':str, 'Board Point': str, 'Off Point': str, 'DOW': str, 
             'New ETD (LT)': str, 'New ETA (LT)': str, 
             'Change code':str, 'Reason':str, 'ProtectToFlt': str}
        
    # Read first sheet:
    df = pd.read_excel(fullFileName, sheet_name=0, parse_dates=['From', 'To'], dtype=dtype)
    df['line_num'] = df.index.values+1
    
    # Bo het dau space, enter:
    df['FLT NBR'] = df['FLT NBR'].str.strip()
    df['FLT NBR'] = df['FLT NBR'].str[2:] # bo QH o dau
    df['Board Point'] = df['Board Point'].str.strip()
    df['Off Point'] = df['Off Point'].str.strip()
    df['Change code'] = df['Change code'].str.strip()

    #df.DOW = df.DOW.str.strip('. ')
    df.DOW = df.DOW.str.replace(r'[. …]', '', regex=True) # ma unicode 8230 (ellipse)
    df.Reason = df.Reason.str.strip()
    
    df.drop(columns=['ServiceType', 'New CFG', 'TAIL #'], inplace=True)
    # Rename columns:
    columnMaps = {'FLT NBR': 'flt', 'Board Point': 'org', 'Off Point': 'dstn',
                  'New ETD (LT)': 'DepTime', 'New ETA (LT)': 'ArrTime',
                  'Change code': 'SCType', 'Reason': 'SCReason'}
    df = df.rename(columns=columnMaps)
    
    df['DepTime'] = df['DepTime'].str[:5] # HH:MM
    df['ArrTime'] = df['ArrTime'].str[:5] # HH:MM
    df.ProtectTo_DC.fillna(0, inplace=True)
    df.ProtectTo_DC = df.ProtectTo_DC.astype(int)
    df.fillna('', inplace=True) # neu change TIM or CNL thi khong co thong tin ACV
    #print(df)
    print(df.columns)
    #return df.to_dict('records') # fastest
    return ConvertDateRange2SingleDate(df)


def ConvertDateRange2SingleDate(df):
    # Chuyen date range trong df thanh tung ngay rieng le
    rows_list = []
    for index, row in df.iterrows():
        depDate = row['From']
        dow = row['DOW'].replace('.', '')
        while depDate <= row['To']:
            dow_depDate = depDate.weekday() + 1
            #print('dow = ', dow, 'dow_depDate = ', dow_depDate)
            if str(dow_depDate) in dow:
                #depDateStr = depDate.strftime("%d-%b-%Y")
                rows_list.append((row['flt'], row['org'], row['dstn'], depDate, dow_depDate,
                         row['DepTime'], row['ArrTime'], row['SCType'], row['SCReason'], row['ProtectToFlt'], row['ProtectToOrg'], 
                         row['ProtectToDstn'], row['ProtectTo_DC'], row['MsgType'], index+2))
                #print(row['etd'].strftime('%H:%M'))
            depDate = depDate + datetime.timedelta(days=1)

    columns_list = ['flt', 'org', 'dstn', 'depDate', 'DOW', 'DepTime', 'ArrTime',
                    'SCType', 'SCReason', 'ProtectToFlt', 'ProtectToOrg', 'ProtectToDstn', 'ProtectTo_DC', 'MsgType', 'line_num']
    newDF = pd.DataFrame(rows_list, columns = columns_list)
    #return newDF.values.tolist()
    #return newDF.T.to_dict()
    
    # Convert newDF to list of dicts:
    #return newDF.T.to_dict().values() # slower 
    return newDF.to_dict('records') # fastest


def readExcel_OCC(fullFileName):
    logStr = 'readExcel_OCC'
    print(logStr)
    logging.warning(logStr)
    
    dtype = {'FLT':str, 'TYPE':str, 'REG':str, 'DEP':str, 'ARR':str, 'CHG CODE':str, 'REASON':str}
    # Read first sheet:
    df = pd.read_excel(fullFileName, sheet_name=0, parse_dates=['DATE', 'ProtectToDate'], dtype=dtype)
        
    # Rename columns:
    columnMaps = {'DATE': 'dptDate', 'FLT': 'flt',  'DEP': 'org', 'ARR': 'dstn',
                  'CHG CODE': 'SCType', 'REASON': 'SCReason'}
    df = df.rename(columns=columnMaps)
    df.fillna('', inplace=True)
    
    df.SCType = df.SCType.str.replace('EQT', 'CON')
    df['line_num'] = df.index.values+1
    
    df.drop(columns=['REG', 'AC', 'STD', 'STA'], inplace=True)
    # Convert df to list of dicts:
    return df.to_dict('records') # fastest


def UTCtoLT(rows):
    #Input: rows: list of dicts
    #   df_utc
    #Output: convert columns dptDate + depTime and dptDate + arrTime of row from UTC to LT    
    logStr = 'UTCtoLT'
    print(logStr)
    logging.warning(logStr)
    
    LT_rows = []
    for row in rows:
        #dptDate dang 30/11/22
        #dptDate_UTC = datetime.datetime.strptime(row['dptDate'] + ' ' + row['depTime'], '%d/%m/%y %H:%M')
        #Chuyen bay bi huy cung co dep/arr time:
        dptDate_UTC = row['dptDate']+datetime.timedelta(hours=int(row['depTime'][:2]), minutes=int(row['depTime'][-2:]))
        dptDate_LT = mylib.UTC2LocalTime(dptDate_UTC, row['org'], df_utc)
        
        #arrDate_UTC = datetime.datetime.strptime(row['dptDate'] + ' ' + row['arrTime'], '%d/%m/%y %H:%M')
        arrDate_UTC = row['dptDate']+datetime.timedelta(hours=int(row['arrTime'][:2]), minutes=int(row['arrTime'][-2:]))
        if arrDate_UTC < dptDate_UTC:
            arrDate_UTC += datetime.timedelta(days=1)
        
        arrDate_LT = mylib.UTC2LocalTime(arrDate_UTC, row['dstn'], df_utc)
        
        row['dptDate'] = datetime.datetime.strftime(dptDate_LT, '%d-%b-%Y')
        row['depTime'] = datetime.datetime.strftime(dptDate_LT, '%H:%M')
        row['arrTime'] = datetime.datetime.strftime(arrDate_LT, '%H:%M')
        
        #print('dptDate_LT, arrDate_LT = ', dptDate_LT, arrDate_LT)
        #row['DOW'] = dptDate_LT.isoweekday()
        if row['SCType'] == 'CNL':
            #print('type = ', type(row['protect_to_date'])) # <class 'pandas._libs.tslibs.timestamps.Timestamp'>
            protect_to_date = row['protect_to_date'].to_pydatetime().date()
            row['dc'] = (protect_to_date - dptDate_LT.date()).days
        else:
            row['dc'] = (arrDate_LT.date() - dptDate_LT.date()).days
            
        LT_rows.append(row)
        
    return LT_rows
    

def copy():
    # To select text, make sure num lock is disabled when using pyautogui
    time.sleep(0.1)
    pa.keyDown('ctrl'); pa.press('c'); pa.keyUp('ctrl') # copy from 1A
    time.sleep(0.1)
    data = cb.paste()
    time.sleep(0.02)
    return data
    

def write(value, interval=0.01):
    pa.write(value, interval = interval)
    time.sleep(0.1)
    pa.hotkey('ctrl', 'a') # select all
    written_value = copy() # copy the written value to check
    if value != written_value:
        logStr = f'Cannot write correctly! Correct value = {value}; Written = {written_value}'
        raise Exception(logStr)


def open_db():
    #Input: 
    #Output: open log db SkdChg.accdb
    
    global access_cursor, access_conn, sql_conn, sql_cursor

    logStr = 'open_db'
    print(logStr)
    logging.warning(logStr)
    
    try:
        # this connection string is for Access 2007, 2010 or later .accdb files
        access_conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+DBfile)
        access_cursor = access_conn.cursor()
    except Exception as e:
        print(e)
        logging.error("Exception occurred", exc_info=True)
        pa.alert(e, title='Skd Change')
    
    # Open SQL Server DB:
    sql_conn, sql_cursor, sql_engine = sql.connect_sqlserver()
       

def init_log_skdchg():
    #Input:
    #Output: open db SkdChg.accdb
    
    global df_utc
    
    mylib.create_log() # open log text file
    
    logStr = '=' * 20 + '\n' + 'init_log_skdchg'
    print(logStr)
    logging.warning(logStr)
           
    # Open Access and SQL Server DB:
    open_db()
       
    #Xoa bang tblSkdChgTemp:
    delete_temp_tables()
    
    #Doc bang tblTimeZone de so sánh thời điểm SC và departure time:
    #query = 'SELECT Airport, TimeZone, NotifyTime, Region, IsDom, TimeZoneCity FROM tblTimeZone'
    #df_utc = sql.exec_sql_return_dataframe(query, 'Airport')
    #df_utc.TimeZone.fillna(float('inf'), inplace=True)
                

def get_log_queries(bStaging):
    #Input: bStaging
    #Output: create query to insert a row in table tblSkdChgTemp or tblSkdChg_Staging

    logStr = 'get_log_queries'
    print(logStr)
    logging.warning(logStr)

    #Danh sach cac cot insert vao bang tblSkdChgTemp:
    columns_list = ['flt', 'org', 'dstn', 'DepDate', 'DOW', 'SCType', 'SCReason', 
        'DepTime', 'ArrTime', 'ProtectToFlt', 'ProtectToOrg', 'ProtectToDstn', 'ProtectTo_DC', 'RunDate', 'RunTime', 
        'Config', 'Aircraft', 'AU_C', 'AU_Y', 'pax_C', 'pax_Y', 'GAV_C', 'GAV_Y', 'Result', 'Reason']

    columns = ",".join(columns_list)
    question_marks = ("?," * len(columns_list))[:-1]
    query_temp = f'INSERT INTO tblSkdChgTemp ({columns}) VALUES ({question_marks})'
    
    #Luu vao bang permanent:
    if bStaging:
        query = f'INSERT INTO tblSkdChg_Staging ({columns}) VALUES ({question_marks})'
    else:
        query = f'INSERT INTO tblSkdChg ({columns}) VALUES ({question_marks})'

    return query, query_temp


def delete_temp_tables():
    #Xoa bang tblSkdChgTemp
    
    logStr = 'delete_temp_tables'
    print(logStr)
    logging.warning(logStr)
    
    try:
        qry = '{call Del_tblSkdChgTemp_Qry()}'
        access_cursor.execute(qry)

        #access_conn.commit()
    except Exception as e:
        print(e)
        logging.error("Exception occurred", exc_info=True)
        pa.alert(e, title='Skd Change')


def close_log():
    # Close Log DB:
    
    logStr = 'close_log'
    print(logStr)
    logging.warning(logStr)
    
    # Close Access DB:
    try:
        if access_conn is not None:
            access_cursor.close()
            access_conn.close()
    except Exception as e:
        print(e)
        logging.error("Exception occurred", exc_info=True)
        pa.alert(e, title='Skd Chg')
    
    # Close SQL Server DB:
    sql.close_sqlserver()
    
    logging.shutdown() # close log text file
    

def insert_skdchg_table(query, query_temp, row):
    #Input: row la 1 list
    #Output: insert a row in table tblSkdChg/tblSkdChg_staging, tblSkdChgTemp of access db, 
    #   and a row in table tblSkdChg/tblSkdChg_staging of SQL Server DB
    
    logStr = 'insert_skdchg_table'
    print(logStr)
    logging.warning(logStr)
    
    try:
        #print(query)
        #print(row)
        #if row la 1 dict thi dung *row.values()
        access_cursor.execute(query, *row)
        # Thu tu cac cot trong row phai dung theo cac tham so trong query
        access_cursor.execute(query_temp, *row)
        access_conn.commit()
        
        # Insert a row in table tblSkdChg or tblSkdChg_staging of SQL Server DB:
        #print('query = ', query)
        #print('values = ', row)
        sql_cursor.execute(query, *row)

        sql_conn.commit()
    except Exception as e:
        print(e)
        logging.error("Exception occurred", exc_info=True)
        pa.alert(e, title='Skd Change')
    
'''
def validate(bKHDB_format, rows, bNewFlt):
    #Input: 
    #   rows la 1 list of dict
    #Output: true if all rows valid
        
    logStr = 'validate'
    print(logStr)
    logging.warning(logStr)

    validate_log_file_name = 'C:/Data/Log/validate.txt'
    validate_fh = open(validate_log_file_name, 'w', encoding='utf-8')        
    
    bOK = True
    
    for rec in rows:
        r = SimpleNamespace(**rec)
        if bKHDB_format:
            if not validate_flt_KHDB(validate_fh, r, bNewFlt): bOK = False
        else:
            if not validate_flt_OCC(validate_fh, r): bOK = False
            
    validate_fh.close()
    
    if not bOK:
        subprocess.call(['notepad.exe', validate_log_file_name])
        logStr = 'Please check log file for error.'
        raise Exception(logStr)        
    

def validate_flt_KHDB(validate_fh, flt_rec, bNewFlt):
    #Input:
    #   validate_fh: log file
    #   flt_rec la 1 record kieu SimpleNamespace
    #Output: true if flt_rec valid
        
    #logStr = 'validate_flt_KHDB'
    #print(logStr)
    #logging.warning(logStr)
    
    bOK = True
    r = flt_rec
    line = r.line_num #line: dong so trong file input
    #print('line, flt_rec = ', line, flt_rec)
    
    if bNewFlt:
        if pd.isna(r.From) or pd.isna(r.To):
            logStr = f'Line {line}: Check From/To Date: cannot empty. Flight: {r.flt}/{r.From}/{r.To}/{r.DOW}'
            bOK = False     
    else:
        if r.dptDate == '':
            logStr = f'Line {line}: Check dptDate: cannot empty. Flight: {r.flt}/{r.dptDate}'
            bOK = False 
    
    if r.DOW == '':
        logStr = f'Line {line}: Check DOW: cannot empty. Flight: {r.flt}/{r.dptDate}'
        bOK = False
    else:
        bOK, logStr = validate_flt(line, flt_rec)
                
    if not bOK:
        #print(logStr)
        validate_fh.write(logStr + '\n')
        #raise Exception(logStr)
        
    return bOK
 

def validate_flt_OCC(validate_fh, flt_rec):
    #Input:
    #   validate_fh: log file
    #   flt_rec la 1 record kieu SimpleNamespace
    #Output: true if flt_rec valid
        
    #logStr = 'validate_flt_OCC'
    #print(logStr)
    #logging.warning(logStr)
    
    if flt_rec.dptDate == '':
        logStr = f'Line {flt_rec.line_num}: Check dptDate: cannot empty. Flight: {flt_rec.flt}'
        bOK = False 
    else:
        bOK, logStr = validate_flt(flt_rec.line_num, flt_rec) #line_num: dong so trong file input
        
    if not bOK:
        #print(logStr)
        validate_fh.write(logStr + '\n')
        #raise Exception(logStr)
        
    return bOK
    
    
def validate_flt(line, flt_rec):
    #Input:
    #   line: dong so trong file input
    #   flt_rec la 1 record kieu SimpleNamespace
    #Output: true if flt_rec valid
    
    bOK = True
    logStr = ''
    r = flt_rec
    
    if r.flt == '' or r.org == '' or r.dstn == '':
        logStr = f'Line {line}: Check flt/org/dstn: cannot empty. Flight: {r.flt}/{r.dptDate}'
        bOK = False
    elif r.SCType == 'NEW' or r.SCType == 'RPL':
        if r.SCType == 'NEW' and r.ServiceType == '':
            logStr = f'Line {line}: Check ServiceType: cannot empty. Flight: {r.flt}/{r.From}/{r.To}/{r.DOW}'
            bOK = False
            
        if r.depTime == '' or r.arrTime == '': # check time:
            logStr = f'Line {line}: Check depTime/arrTime: cannot empty. Flight: {r.flt}/{r.dptDate}'
            bOK = False
        elif r.AcvCode =='' or r.SaleCode == '': # check config:
            logStr = f'Line {line}: Check AcvCode/SaleCode: cannot empty. Flight: {r.flt}/'
            if r.SCType == 'RPL':   
                logStr += f'{r.dptDate}'
            else: # NEW
                logStr += f'{r.From}/{r.To}/{r.DOW}'                
            bOK = False
    elif r.SCType == 'TIM': # change time
        if r.depTime == '' or r.arrTime == '':
            logStr = f'Line {line}: Check depTime/arrTime: cannot empty. Flight: {r.flt}/{r.dptDate}'
            bOK = False
    elif r.SCType == 'CON': # change config
        if r.AcvCode =='' or r.SaleCode == '':
            logStr = f'Line {line}: Check AcvCode/SaleCode: cannot empty. Flight: {r.flt}/{r.dptDate}'
            bOK = False
    elif r.SCType == 'CNL': # cancel flt
        if r.protect_to_flt == '':
            logStr = f'Line {line}: Check protect_to_flt: cannot empty. Flight: {r.flt}/{r.dptDate}'
            bOK = False
                
    return bOK, logStr


def get_protect_flt(flt, dptDate, org, dstn, dptTime, protect_to_flt, dc):
    logStr = 'get_protect_flt'
    print(logStr)
    logging.warning(logStr)
    
    if protect_to_flt == '': # No protect
        protect_to = ()
    else: # Protect
        protect_to_arr = protect_to_flt.split(';')
        dc_arr = dc.split(';')                
        if len(dc_arr) == 1 and len(protect_to_arr) == 1:
            protect_to_flt = protect_to_arr[0][2:] # bo QH o dau
            prot_to_dep_date = mylib.add_day(dptDate, int(float(dc_arr[0])))
            prot_to_dep_time = dptTime # user nhap depTime cua protect_to_flt vao o depTime cua chuyen bi huy 

            protect_to = (protect_to_flt, prot_to_dep_date, org, dstn, prot_to_dep_time)
        else:
            protect_to = ()
            
    return protect_to


def IsScWithin24hAndNotifyTime(dptDate, depTime, orgAirport, destAirport):
    #Input: dptDate, depTime, orgAirport, destAirport: 
    #   dptDate dang: '30-Mar-2021', depTime dang '12:30'
    #   Voi chuyen doi TIM thi depTime la gio moi tren dien
    #   Voi chuyen doi CON, CNL thi depTime la gio hien tai cua chuyen bay
    #Output:    
    #   if NotifyTime (hours) < (dptDate + depTime) - RunTime <= 24: return True
    # Xem IsPassNotifyTime
    
    logStr = 'IsScWithin24hAndNotifyTime'
    print(logStr)
    logging.warning(logStr)
        
    #row = df_utc[df_utc['Airport'] == orgAirport]
    #notify_minutes = int(row.iloc[0]['NotifyTime']) # cast from numpy.int64 to int    
    if orgAirport in df_utc.index:
        TimeZone = int(df_utc.loc[orgAirport, 'TimeZone'])
        org_notify_minutes = int(df_utc.loc[orgAirport, 'NotifyTime']) # cast from numpy.int64 to int
    else:
        logStr = f'Cannot find airport {orgAirport} in table tblTimeZone!'
        raise Exception(logStr)
        
    if destAirport in df_utc.index:
        dest_notify_minutes = int(df_utc.loc[destAirport, 'NotifyTime'])
    else:
        logStr = f'Cannot find airport {destAirport} in table tblTimeZone!'
        raise Exception(logStr)
        
    notify_hours = max(org_notify_minutes, dest_notify_minutes) / 60

    dptDateStr = dptDate + ' ' + depTime
    cur_dep_time = datetime.datetime.strptime(dptDateStr, '%d-%b-%Y %H:%M')
    #cur_dep_time_utc = mylib.LocalTime2UTC(cur_dep_time, int(row.iloc[0]['TimeZone']))
    cur_dep_time_utc = mylib.LocalTime2UTC(cur_dep_time, TimeZone)
    
    #cur_dep_time_utc_minus_notify_minutes = cur_dep_time_utc + datetime.timedelta(minutes=-notify_minutes)
    
    # This script is run in HaNoi --> UTC+7:
    cur_time_utc = mylib.LocalTime2UTC(datetime.datetime.now(), 7) # now tinh theo UTC
   
    # 'Jun 1 2005  1:33PM', '%b %d %Y' %I:%M%p'    
    diff = cur_dep_time_utc - cur_time_utc # dep_time tinh theo UTC
    
    diff_in_hours = diff.days * 24 + diff.seconds / 3600
    return (diff_in_hours <= 24 and diff_in_hours > notify_hours) , diff_in_hours
'''
