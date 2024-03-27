'''
#https://stackoverflow.com/questions/33725862/connecting-to-microsoft-sql-server-using-python
# PROVIDER
import adodbapi
conn = adodbapi.connect("PROVIDER=SQLOLEDB;Data Source={0};Database={1}; \
       trusted_connection=yes;UID={2};PWD={3};".format(ServerName,MSQLDatabase,username,password))
cursor = conn.cursor()
'''

# DRIVER

import pyodbc
import pandas as pd
from sqlalchemy import create_engine
import logging
#import pyautogui as pa

conn = cursor = sql_engine = 0

def connect_sqlserver():
    DB = 'TicketRefund'
    #ServerName = '172.19.17.218\scc' 
    #user = 'sa' 
    #password = 'NgocAnh@123'
    
    #ServerName = '103.139.41.25' 
    #user = 'User_Maureva' 
    #password = 'p!#aqC4XoVd5cE$'
    
    ServerName = '103.229.41.128' 
    user = 'TicketRefund' 
    password = 'Donottry@123'
    
    conn_str = "DRIVER={{SQL Server Native Client 11.0}};SERVER={0}; database={1}; \
          trusted_connection=no;UID={2};PWD={3}".format(ServerName,DB, user, password)
    
    logStr = 'connect_sqlserver'
    print(logStr)
    logging.warning(logStr)
    
    global conn, cursor, sql_engine
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
    except Exception as e:
        print(e)
        logging.error("Exception occurred", exc_info=True)
        raise Exception("connect_sqlserver")
    
    '''
    cursor.execute('SELECT * FROM Table')
    for row in cursor:
        print('row = %r' % (row,))
        
    cursor.execute(sql)
    data = cursor.fetchall()   
    df = pandas.DataFrame(data)    
    '''
    
    sql_engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(conn_str))
    return conn, cursor, sql_engine


def close_sqlserver():
    logStr = 'close_sqlserver'
    print(logStr)
    logging.warning(logStr)

    try:
        if conn is not None:
            cursor.close()
            conn.close();
    except Exception as e:
        print(e)
        logging.error("Exception occurred", exc_info=True)


def exec_sql_return_dataframe(sql, index_col=None):
    logStr = 'exec_sql_return_dataframe'
    print(logStr)
    logging.warning(logStr)

    if index_col is None:
        df = pd.read_sql(sql, sql_engine)
    else:
        df = pd.read_sql(sql, sql_engine, index_col=[index_col])
    #df = pd.read_sql_query(sql, sql_engine, chunksize=10**6)
        
    #df = pd.DataFrame.from_records(cursor.execute(sql).fetchall(), columns=[desc[0] for desc in cursor.description])
    return df
    

def exec_sql_return_dict(sql):
    logStr = 'exec_sql_return_dict'
    print(logStr)
    logging.warning(logStr)
    
    df = pd.read_sql(sql, sql_engine)
    #print(df)
    return df.to_dict('records') 


def exec_sql_return_dict_NotUsed(sql, columns_str):
    logStr = 'exec_sql_return_dict'
    print(logStr)
    logging.warning(logStr)

    cursor.execute(sql)
    my_data = cursor.fetchall()
    rows_list = []
    for row in my_data:
        #print('type row = ', type(row)) # type row =  <class 'pyodbc.Row'>
        rows_list.append(tuple(row)) # convert pyodbc.Row to tuple
        
    columns_list = columns_str.split(',')   
    #print('rows_list = ', rows_list)
    df = pd.DataFrame(data=rows_list, columns=columns_list)
    #print(df)
    return df.to_dict('records') 
    
    
def exec_sql_return_tuple(sql):
    logStr = 'exec_sql_return_tuple'
    print(logStr)
    logging.warning(logStr)
    
    cursor.execute(sql)
    rows = ()
    for row in cursor:
        print('row = %r' % (row,))
        rows.append((row,))
        
    return rows
        
     
def exec_sql(sql):
    #Execute Delete Statement
    logStr = 'exec_sql'
    print(logStr)
    logging.warning(logStr)
    
    result = cursor.execute(sql)
    #print('result = ', result)
    conn.commit()

    
def exec_store_proc(proc_name, paras):
    #Input: conn, proc_name, paras
    #   paras: 1 list
    #Output: dataframe
    
    logStr = 'exec_store_proc'
    print(logStr)
    logging.warning(logStr)
    
    if paras == None:
        sql = 'exec dbo.' + proc_name
        df = pd.read_sql_query(sql, conn)
    else:
        question_marks = ' ' + (',?' * len(paras))[1:]
        sql = 'exec dbo.' + proc_name + question_marks    
        #df = pd.read_sql_query('exec dbo.usp_GetPatientProfile ?', cnxn, params=['MyParam'] ) 
        df = pd.read_sql_query(sql, conn, params = paras)
        
    return df
    

'''
def remove_existed_pnrs_in_strip_table(df, bStaging):
    #Input: 
    #   df chua cac PNR trong strip file
    #   bStaging: run SC on Staging or Production env
    #Output: 
    # Delete table tblStrip or tblStrip_Staging that have same PNR, PNRCreationDate, flt, dptDate of Sql Server DB to avoid dup insert pax
    
    logStr = 'remove_existed_pnrs_in_strip_table'
    print(logStr)
    logging.warning(logStr)
        
    #print('df.columns = ', df.columns)    
    #rlocs = df['PNR #'].unique()
    df_rloc = df[['PNR', 'PnrCreationDate', 'flt', 'dptDate']]
    df_rloc = df_rloc.drop_duplicates()
    
    if bStaging:
        query = 'Select Count(*) From tblStrip_Staging Where PNR=? And PnrCreationDate=? And flt=? And dptDate=?'
    else:
        query = 'Select Count(*) From tblStrip Where PNR=? And PnrCreationDate=? And flt=? And dptDate=?'
        
    for row in df_rloc.itertuples():
        cursor.execute(query, row.PNR, row.PnrCreationDate, row.flt, row.dptDate)
        count = cursor.fetchone()[0]
        if count > 0:
            index = df[(df.PNR == row.PNR) & (df.PnrCreationDate == row.PnrCreationDate) & (df.flt == row.flt) & (df.dptDate == row.dptDate)].index
            df.drop(index, inplace=True)
        #conn.commit() # commit ngay de tranh bi deadlock giua 2 clients cung chay
'''
    
    
def SaveStripTable(df_strip, bStaging):  
    #If bStaging = false:
        #Copy table tblStripTemp (df_strip) to table tblStrip in SqlServer TicketRefund DB
    #Else:
        #Copy table tblStripTemp (df_strip) to table tblStrip_Staging in SqlServer TicketRefund DB
    
    logStr = 'SaveStripTable'
    print(logStr)
    logging.warning(logStr)
    
    try:       
        #remove_existed_pnrs_in_strip_table(df_strip, bStaging)
        
        if bStaging:
            df_strip.to_sql('tblStrip_Staging', schema='dbo', con=sql_engine, index=False, if_exists='append') # chunksize = 2100 / 34 = 61
        else:
            df_strip.to_sql('tblStrip', schema='dbo', con=sql_engine, index=False, if_exists='append')        
    except Exception as e:
        print(e)
        logging.error("Exception occurred", exc_info=True)
        raise Exception("SaveStripTable")

   

if __name__ == '__main__':
    conn, cursor, sql_engine = connect_sqlserver()   
        
    df = exec_store_proc('IsPnrExistIntblStrip_NotUsed', ('123456', '01-Apr-2021'))
    print('df = ', df)
    print('value = ', df.loc[0, 'NumPax'])
    '''
    DBfile = 'C:/Data/SkdChg.accdb'
    access_conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+DBfile)
    df_sc = pd.read_sql('Select * From tblSkdChgTemp', access_conn)
    df_strip = pd.read_sql('Select * From tblStripTemp', access_conn)
    #df_strip = pd.read_csv("C:/Data/strip.csv", sep=',', header=0) 
    print('df_strip shape = ', df_strip.shape)        
    
    access_conn.close()
    '''
    
    # RefundCheck 'GR2A3Z', 'MR', 'NTBA', 'NTBA5' 
    
    df = exec_sql_return_dataframe('SELECT * FROM tblTimeZone')
    print(df)
    
    df1 = exec_sql_return_dict('SELECT * FROM AspNetUsers')
    print(df1)
    
    close_sqlserver()
