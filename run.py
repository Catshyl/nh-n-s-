import pyautogui as pa
from types import SimpleNamespace
import logging
import datetime
import time

import cursor
import config  # import global variables
import lib_win
import mylib
import SkdChg as Res


search_set_win = ('imgs/search_set_win.jpg', (),(), 'Search SET Items')
NoSetItem_win = ('imgs/NoSetItem_win.jpg', (), (), 'No SET item found.')
Reac_Solution_win = ('imgs/Reac_Solution_win.jpg', (), (), 'Re-accomodation Solution')
NoChangeFromCurrentSchedule_win = ('imgs/NoChangeFromCurrentSchedule_win.jpg', (), (), 'No change from the current schedule. Do you still want to accept?')

timeout = 60 # seconds


def RunSC(bKHDB_Format, fullFileName, bStaging):
    #Input: bKHDB_Format, fullFileName Excel file chua SC 
    #       if bStaging = true: run tren he staging
    #       else: run tren he production
    
    # main SC
    #if pa.confirm(text='Are you sure to skip check VIP?\nTurn off CapLock and Unikey', title='Auto SC', buttons=['Yes', 'No']) == 'No':
    #    return
        
    # Turn off Capslock and NumLock keyboards:
    #config.turn_off_capslock_numlock_key()
    
    print('RunSC')
    
    Res.bStaging = bStaging
    
    #Click vao ung dung Inventory cua 1A:
    pa.click(config.window_title_pos)
    time.sleep(0.1)
    
    try:
        lib_win.init_log_skdchg() # open log DB

        if bKHDB_Format:
            rows = lib_win.readExcel_KHDB(fullFileName)
        else:
            rows = lib_win.readExcel_OCC(fullFileName)
            #rows = lib_win.UTCtoLT(rows)

        #lib_win.validate(bKHDB_Format, rows)
        #print(rows)
        win_search_set_pos = open_window_search_set()
        #exit()
        bFirstRow = True
        for row in rows:
            r = SimpleNamespace(**row)
            print(row)
            depDateStr = mylib.date2str2(r.depDate)
            logStr = '-' * 10 + '\n' + ';'.join(str(x) for x in row.values())
            print(logStr)
            logging.warning(logStr)
            
            if not bFirstRow:
                pa.keyDown('alt'); pa.press('e'); pa.keyUp('alt') # New Search button
                lib_win.wait_until_window_open(search_set_win, timeout)
                pa.press('tab') # move to Airline Code box
                time.sleep(0.01)
            bFirstRow = False

            if not display_flt_date(r.flt, depDateStr, depDateStr): continue # next flt
            pa.moveTo(Res.center_scr)
            pa.keyDown('alt'); pa.press('c'); pa.keyUp('alt') # Accept button
            cursor.wait_cursor('ARROW', timeout)
            time.sleep(0.1)
            #After Accept button, window SET remains on screen, but the flight disappears

            if r.SCType == 'CON' or r.SCType == 'TIM':
                #After Accept button, window Re-Accommodation Solution open
                if pa.locateOnScreen(NoChangeFromCurrentSchedule_win[0], grayscale=True, confidence=0.9) is not None:
                    logStr = NoChangeFromCurrentSchedule_win[3]
                    print(logStr)
                    logging.warning(logStr)
                    pa.press('enter')
                    cursor.wait_cursor('ARROW', timeout)
                    continue # next flt

                if r.SCType == 'CON':
                    #Get Inventory of flt/date:
                    inven = Res.change_config(r)
                    
                    r.Config = inven['Config']
                    r.Aircraft = inven['Aircraft']
                    r.AU_C = inven['AU_C']
                    r.AU_Y = inven['AU_Y']
                    r.pax_c = inven['Bkg_C']
                    r.pax_y = inven['Bkg_Y']
                    r.avail_c = inven['GAV_C']
                    r.avail_y = inven['GAV_Y']
                    r.Reason = 'Overbook' if r.pax_c > r.avail_c or r.pax_y > r.avail_y else ''
                else: # TIM
                    lib_win.wait_until_window_open(Reac_Solution_win, timeout)
                    bkg, avail = Res.change_time()
                    r.Config = r.Aircraft = ''
                    r.AU_C = r.AU_Y = 0
                    r.pax_c = bkg['C']
                    r.pax_y = bkg['Y']
                    r.avail_c = avail['C']
                    r.avail_y = avail['Y']
                    r.Reason = ''
                    
                r.Result = 'OK'

            elif r.SCType == 'CNL':
                pa.moveTo(Res.center_scr)
                pa.keyDown('alt'); pa.press('c'); pa.keyUp('alt') # Accept button
                cursor.wait_cursor('ARROW', timeout)
                time.sleep(0.1)

                #After Accept button: window Re-Accommodation Solution open
                if r.ProtectTo_DC != 0:
                    ProtectToDate = mylib.date2str2(mylib.add_day2(r.depDate, r.ProtectTo_DC))
                else:
                    ProtectToDate = depDateStr

                bOK, bkg, avail = Res.cancel_flt(r.ProtectToFlt, ProtectToDate, r.ProtectToOrg, r.ProtectToDstn)

                #r1 = SimpleNamespace(**vars(r)) # r1 is a copy of r. vars() function returns the __dict__ attribute of an object
                #r1 = SimpleNamespace(**r.__dict__)
                
                r.Config = r.Aircraft = ''
                r.AU_C = r.AU_Y = 0
                r.pax_c = bkg['C']
                r.pax_y = bkg['Y']
                r.avail_c = avail['C']
                r.avail_y = avail['Y']
                if bOK:
                    r.Result = 'OK'
                    if r.ProtectToFlt == 'NON':
                        r.Reason = ''
                    else:
                        r.Reason = 'Overbook' if r.pax_c > r.avail_c or r.pax_y > r.avail_y else ''
                else:
                    r.Result = 'Not OK'
                    r.Reason = Res.logStr
            else: # other case: not process any thing
                raise Exception(f'Invalid SCType {r.SCType}')
                
            #write table tblSkdChgTemp:
            CopyFltToDb(r, bStaging) # phai ghi depDate va pax C/Y

            if config.bStop:
                logStr = 'You manually Stop! SC must be run again from begining'
                print(logStr)
                logging.warning(logStr)
                break

            time.sleep(0.5)
    
    except Exception as e:
        #err = NameError("name 'time' is not defined")       
        print(e)
        logging.error("Exception occurred", exc_info=True)
        pa.alert(e, title='Skd Change') 
    #finally: # always executed
        
    lib_win.close_log() # close log DB


def open_window_search_set():
    # Alt + 1 --> s
    global logStr
    logStr = 'open_window_search_set'
    print(logStr)
    logging.warning(logStr)
    
    pa.keyDown('alt'); pa.press('1'); pa.keyUp('alt') # Schedule & Re-Accommodation
    pa.press('s')
    return lib_win.wait_until_window_open(search_set_win, timeout)


def display_flt_date(flt, dptDateFrom, dptDateTo):
    #In window Search SET Items
    #Input: write flt, dptDateFrom, dptDateTo then press Search
    #Output: open window SET
    
    logStr = 'display_flt_date'
    print(logStr)
    logging.warning(logStr)
    
    pa.press('tab') # move to Flight Ranges box
    time.sleep(0.01)
    pa.write(flt)
        
    pa.press('tab')
    time.sleep(0.01)
    pa.write(dptDateFrom)
    
    pa.press('tab')
    time.sleep(0.01)
    pa.write(dptDateTo)
    
    pa.press('enter') # Search
    time.sleep(0.01)
    cursor.wait_cursor('ARROW', timeout)

    bOk = pa.locateOnScreen(NoSetItem_win[0], grayscale=True, confidence=0.9) is None # True if flt found
    if not bOk:
        print(NoSetItem_win[3])
        logging.warning(NoSetItem_win[3])
        pa.press('tab') # Cancel button
        time.sleep(0.01)
        pa.press('enter') 
        time.sleep(0.01)
    return bOk


def CopyFltToDb(r, bStaging):
    #Input: r, bStaging
    #Output: copy to local MS Access va SQL Server DB flight da run SC

    logStr = 'CopyFltToDb'
    print(logStr)
    logging.warning(logStr)

    r.RunDate = datetime.date.today().strftime("%Y-%b-%d")
    r.RunTime = datetime.datetime.now().strftime("%H:%M:%S")

    #print('r = ', r)
    #Ghi log vao local MS Access va SQL Server DB: da xac dinh env: staging hay production: table tblSkdChg:
    query, query_temp = lib_win.get_log_queries(bStaging)
    #['flt', 'org', 'dstn', 'DepDate', 'DOW', 'SCType', 'SCReason', 'DepTime', 'ArrTime', 'ProtectToFlt', 'ProtectToOrg', 'ProtectToDstn', 'ProtectTo_DC', 'RunDate', 'RunTime', 'Config', 'Aircraft', 'AU_C', 'AU_Y', 'pax_C', 'pax_Y', 'GAV_C', 'GAV_Y', 'Result', 'Reason']
    
    ProtectToFlt = r.ProtectToFlt if r.ProtectToFlt == 'NON' else r.ProtectToFlt[2:]
    
    insert_row = [r.flt, r.org, r.dstn, r.depDate, r.DOW, r.SCType, r.SCReason, \
        r.DepTime, r.ArrTime, ProtectToFlt, r.ProtectToOrg, r.ProtectToDstn, r.ProtectTo_DC, r.RunDate, r.RunTime, \
        r.Config, r.Aircraft, r.AU_C, r.AU_Y, r.pax_c, r.pax_y, r.avail_c, r.avail_y, \
        r.Result, r.Reason]

    lib_win.insert_skdchg_table(query, query_temp, insert_row)


if __name__ == '__main__':
    bKHDB_Format =True
    fullFileName = 'Input.xlsx'
    bStaging = True
    
    RunSC(bKHDB_Format, fullFileName, bStaging)
