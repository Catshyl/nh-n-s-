# Thay doi lich bay tren he thong RES
# Work in screen resolution: width=1366, height=768

# Khi copy version moi thi chay:
# xcopy source [destination] /d /s /y

from types import SimpleNamespace
import pyautogui as pa
import datetime
import time
import logging
import re
import clipboard as cb

import cursor
import lib_win
import mylib

#De reload module: python version >= 3.4
#import importlib
#importlib.reload(module)


UpdateDefaultOption_win = ('imgs/UpdateDefaultOption_win.jpg', (), (), 'Update Default Option')
AutomaticFlightSelection_win = ('imgs/AutomaticFlightSelection_win.jpg', (), (), 'Automatic Flight Selection')
SaveChanges_win = ('imgs/SaveChanges_win.jpg', (), (), 'Do you want to save your changes?')
CreatePaxListOption_win = ('imgs/CreatePaxListOption_win.jpg', (), (), 'Create Passengers List Option')
CommitError_win = ('imgs/CommitError_win.jpg', (), (), 'Default Option: Flight cannot be locked')

CancelNoOptionCreated_win = ('imgs/CancelNoOptionCreated_win.jpg', (), (), 'No valid option created')
CancelRequestedConfirm_win = ('imgs/CancelRequestedConfirm_win.jpg', (), (), 'Cancel Requested. Are you sure you want to cancel the current re-accommodation?')
SearchFlightDate_win = ('imgs/SearchFlightDate_win.jpg', (), (), 'Search Flight Date')
SaveOption_win = ('imgs/SaveOption_win.jpg', (), (), 'Do you want to Save the option ?')

ReaccCancelButton = 'imgs/ReaccCancelButton.jpg'

NoPnrRetrieve_win = 'imgs/NoPnrRetrieve_win.jpg'
OK_Button = 'imgs/OK_Button.jpg' # nut OK cua window Re-accommodation Solution
Selected_Flt_Cell = 'imgs/Selected_Flt_Cell.jpg'
Selected_FltStatus_Cell = 'imgs/Selected_FltStatus_Cell.jpg'

#end_list_grid = 'imgs/end_list_grid.jpg'
reac_OnlyDefaultOptionFlt_cell = 'imgs/reac_OnlyDefaultOptionFlt_cell.jpg'

end_of_list  ='imgs/end_of_list.jpg'
end_of_list2 ='imgs/end_of_list2.jpg'

add_all_rloc_btn_pos = (850, 426)

timeout = 60 # seconds

logStr = ''
w, h = pa.size()
center_scr = (w//2, h//2)

bStaging = False


def get_availability():
    #Input: in window Re-Accommodation QH flt/dptDate
    
    #Output:
    #   open window Availability
    #   bkg, avail cua compartment C, Y
    
    logStr = 'get_availability'
    print(logStr)
    logging.warning(logStr)

    # menu Tools --> Availability:
    pa.keyDown('alt'); pa.press('o'); pa.keyUp('alt')
    pa.press('v') # window Availability open
    cursor.wait_cursor('ARROW', timeout)
    
    #Move to grid FROM Segment Bookings:
    for _ in range(2):
        pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl')
        time.sleep(0.01)
    
    data = lib_win.copy()
    #print('FROM = ', data)
    arr = data.split('\t')
    #print(arr) # ['QH 0174\r\n', 'SGN-DAD\r\n', '10Jul23\r\n', 'C\r\nY\r\n', '0\r\n1\r\n']
    #print('arr = ', arr)
    arr1 = arr[-1].strip().split('\r\n')
    #print('arr1 = ', arr1)
    bkg = {}
    bkg['C'] = int(arr1[0])
    bkg['Y'] = int(arr1[1])
    
    pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl') #move to grid TO Flights Availability
    data = lib_win.copy()
    #print('TO = ', data)

    arr = data.split('\t')
    #print(arr) # ['QH 0225\r\n', 'SGN-DAD\r\n', '10Jul23\r\n', 'C\r\nY\r\n', '26\r\n268\r\n', '26\r\n268\r\n', '26\r\n268\r\n', '26\r\n268\r\n']
    arr1 = arr[-1].strip().split('\r\n')
    #print('arr1 = ', arr1)
    
    avail = {}
    if len(arr1) > 1:
        avail['C'] = max(0, int(arr1[0])) # so < 0 thi chuyen thanh 0
        avail['Y'] = max(0, int(arr1[1]))
    else:
        avail['C'] = avail['Y'] = 0
        
    pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl') #move to Close button --> close window Availability
    pa.press('enter')

    return bkg, avail


def find_prot_to_flt(flt, dptDate):
    #In window Automatic Flight Selection
    #Input: flt, dptDate : prot to flt
    #Output: tim flt/date trong Proposed Solution trung voi flt, dptDate
    
    logStr = 'find_prot_to_flt'
    print(logStr)
    logging.warning(logStr)
    
    for _ in range(3):
        pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl') #move to grid Proposed Solutions
        time.sleep(0.01)

    pa.press('down') # move to default option flt
    fltnbr = depDate = ''
    
    #Loop press down to find flights so background color changed:
    while fltnbr != flt or depDate != dptDate:
        pa.press('down')
        #time.sleep(0.01)
        data = lib_win.copy()
        #print('data = ', data)
        
        arr = data.split('\t')
        if len(arr) < 4:
            raise Exception('find_prot_to_flt: Error: Cannot get flt/date to protect pax!')
            
        fltnbr = arr[1].strip()[3:] # bo 'QH '
        depDate = arr[2].strip()
        
    box = pa.locateOnScreen(Selected_Flt_Cell, grayscale=True, confidence=0.99) # confidence must be very high
    if box is None:
        raise Exception('Cannot find Selected_Flt_Cell!')
        
    y = pa.center(box)[1] # lay toa do y
    box = pa.locateOnScreen(Selected_FltStatus_Cell, grayscale=True, confidence=0.99,region = (783, y-10, 41, 26)) # region: left, top, width, height
    if box is None:
        raise Exception('Flight Status is not OK!') # status is locked or not avail

    pa.click(449, y) # click on circle box (Selected Solutions) to select flight
    
    #color = (255, 228, 161) # selected background color
    #begin_pos = (413, 452)
    #end_pos = (431, 644)
    #pos = get_row_pos(begin_pos, end_pos, color)
    #pa.click(449, pos[1])


'''
def get_row_pos(start=(0,0), end=(50,50), color=(255, 228, 161)): 
    #Input: start, end, color
        #color: (r,g,b) value

    logStr = 'get_row_pos'
    print(logStr)
    logging.warning(logStr)
    
    num_pixels_found = 0 #nothing found yet 
    num_y = 14
    ratio = 0
    pos = (0, 0)
    
    width = end[0] - start[0]
    height = end[1] - start[1]
    s = pa.screenshot(region=(start[0], start[1], width, height))
    for x in range(width): #loops through x value
        for y in range(height): #loops through y value
            p = s.getpixel((x, y))
            if p == color: #checks if the wanted RGB value is in the region
                num_pixels_found = 0
                for x1 in range(x, width):
                    for y1 in range(y, y + num_y): # 1 row cao khoang 14 pixel
                        p = s.getpixel((x1, y1))
                        if p == color:
                            num_pixels_found += 1 #adds one to the result
                
                num_x = width - x
                
                ratio = num_pixels_found / (num_x * num_y)
                print('num_pixels_found = ', num_pixels_found, ', ratio = ', ratio)
                if ratio > 0.9: 
                    pos = (x + start[0], y + num_y//2 + start[1])
                    break
                
        if ratio > 0.9: break
        
    print('ratio = ', ratio)
    print('pos = ', pos)
    return pos
'''


def get_prot_to_flts(overbook):
    #In window Automatic Flight Selection
    #Input: overbook
    #Output: Ok and list of prot_to_flt
    
    logStr = 'get_prot_to_flts'
    print(logStr)
    logging.warning(logStr)
    
    for _ in range(3):
        pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl') #move to grid Proposed Solutions
        time.sleep(0.01)
        
    pa.press('down') # move to default option flt
    prot_to_flts = []
    bOk = False
    total_avail_C = total_avail_Y = 0
    cur_fltnbr = cur_dptDate = ''
    bFirstFlt = True
    
    #Loop press down to find flights:
    while total_avail_C < overbook['C'] or total_avail_Y < overbook['Y']:
        pa.press('down')
        time.sleep(0.01)
        if bFirstFlt:
            if pa.locateOnScreen(reac_OnlyDefaultOptionFlt_cell, grayscale=False, confidence=0.9) is not None:
                #Proposed Solution: has only Default Option Flight:
                return bOk, prot_to_flts
            bFirstFlt = False

        box = pa.locateOnScreen(Selected_Flt_Cell, grayscale=True, confidence=0.99) # confidence must be very high
        if box is None:
            raise Exception('Cannot find Selected_Flt_Cell!')
        y = pa.center(box)[1] # lay toa do y
        box = pa.locateOnScreen(Selected_FltStatus_Cell, grayscale=True, confidence=0.99,region = (783, y-10, 41, 26)) 
        # region: left, top, width, height
        if box is None: # khong tim thay status la dau check box xanh (OK)
            continue # move to next row # status is locked or not avail

        data = lib_win.copy()
        #print('data = ', data)
        
        arr = data.split('\t')
        fltnbr = arr[1].strip()[3:] # bo 'QH '
        dptDate = arr[2].strip()
        if cur_fltnbr == fltnbr and cur_dptDate == dptDate: # already at last row
            break
            
        avail_C = int(arr[-3])
        avail_Y = int(arr[-2])
        #print(f'fltnbr = {fltnbr}, {dptDate}, {avail_C}, {avail_Y}')

        if avail_C > 0 or avail_Y > 0:
            flt = {}
            flt['flt'] = fltnbr
            flt['dptDate'] = dptDate
            flt['avail_C'] = avail_C
            total_avail_C += avail_C
            
            flt['avail_Y'] = avail_Y
            total_avail_Y += avail_Y

            prot_to_flts.append(flt)
            
        cur_fltnbr = fltnbr
        cur_dptDate = dptDate
        
    bOk = total_avail_C >= overbook['C'] and total_avail_Y >= overbook['Y']
    
    return bOk, prot_to_flts


def get_in_outbound_rlocs():
    #In window Create Passengers List Option 1
    #Output: list of rloc of pax has inbound or outbound
    # dung Add button de xac dinh duoc so khach
    
    logStr = 'get_in_outbound_rlocs'
    print(logStr)
    logging.warning(logStr)
    
    total_num_pax = 0
    in_outbound_rlocs = []
    
    pa.keyDown('alt'); pa.press('r'); pa.keyUp('alt') # button Retrieve Passenger List
    cursor.wait_cursor('ARROW', timeout)
    # window Retrieve Passenger List open
    
    for _ in range(2):
        pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl') # move to combo box Passenger List
        time.sleep(0.01)
    pa.press('i') # chọn Inbound or Outbound Passengers
    time.sleep(0.01)
    pa.press('tab') # move to Retrieve button
    time.sleep(0.01)
    pa.press('enter')
    cursor.wait_cursor('ARROW', timeout)
    #time.sleep(1)
    if pa.locateOnScreen(NoPnrRetrieve_win, grayscale=True, confidence=0.9) is not None:
        pa.press('enter') # OK button to close window
        time.sleep(0.01)
        pa.press('esc') # Cancel button to close window Retrieve Passenger List
        time.sleep(0.01)
        return total_num_pax, in_outbound_rlocs

    #Move each rloc to Selected PNR List combo box:
    pa.click(319, 304) # first cell of Available Passengers List combo box
    time.sleep(0.01)
    #Chọn các PNR theo thứ tự từ dưới lên trên
    pa.keyDown('ctrl'); pa.press('end'); pa.keyUp('ctrl') # move to bottom row
    time.sleep(0.01)

    while True:
        data = lib_win.copy() # 53MTXV,TEST,C,2,HK,false
        arr = data.split(',')
        rloc = arr[0]
        if rloc not in in_outbound_rlocs:
            num_pax = int(arr[3])
            #print(f'rloc = {rloc}, num_pax = {num_pax}')

            pa.keyDown('alt'); pa.press('a'); pa.keyUp('alt') # button Add to move rloc to Selected PNR List
            time.sleep(0.01)
            in_outbound_rlocs.append(rloc)
            total_num_pax += num_pax

            #Move focus back to Available Passengers List combo box:
            pa.click(925, 304) # click to first row of Selected PNR List
            time.sleep(0.01)
            for _ in range(4):
                pa.hotkey('ctrl', 'shift', 'tab')
                time.sleep(0.01)

        if pa.locateOnScreen(end_of_list, region=scrbar_region, grayscale=False, confidence=0.98) is not None or \
           pa.locateOnScreen(end_of_list2, region=scrbar_region2, grayscale=False, confidence=0.98) is not None:
            break # end of rloc list

        #pa.press('up', presses= num_pax,interval=0.01) # next below rloc
        pa.press('up')

    print('total_num_pax = ', total_num_pax)
    print('in_outbound_rlocs = ', in_outbound_rlocs)
    pa.click(1087, 665) # Cancel button to close window Retrieve Passenger List
    time.sleep(0.1)
    #Window "Do you want to save your changes?" open
    pa.press('tab') # No button
    time.sleep(0.01)
    pa.press('enter')
    time.sleep(0.1)
    
    return total_num_pax, in_outbound_rlocs

'''
def get_in_outbound_rlocs_old():
    #In window Create Passengers List Option 1
    #Output: list of rloc of pax has inbound or outbound
    # dung Add All button --> khong xac dinh duoc so khach
    
    logStr = 'get_in_outbound_rlocs'
    print(logStr)
    logging.warning(logStr)
    
    total_pax_inout_bound = 0
    in_outbound_rlocs = []

    pa.keyDown('alt'); pa.press('r'); pa.keyUp('alt') # button Retrieve Passenger List
    cursor.wait_cursor('ARROW', timeout)
    # window Retrieve Passenger List open
    
    for _ in range(2):
        pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl') # move to combo box Passenger List
        time.sleep(0.01)
    pa.press('i') # chọn Inbound or Outbound Passengers
    time.sleep(0.01)
    pa.press('tab') # move to Retrieve button
    time.sleep(0.01)
    pa.press('enter')
    cursor.wait_cursor('ARROW', timeout)
    time.sleep(1)
    if pa.locateOnScreen(NoPnrRetrieve_win, grayscale=True, confidence=0.9) is not None:
        pa.press('enter') # OK button to close window
        time.sleep(0.01)
        pa.press('esc') # Cancel button to close window Retrieve Passenger List
        time.sleep(0.1)
        return total_pax_inout_bound, in_outbound_rlocs
        
    #Get all rlocs:
    pa.click(add_all_rloc_btn_pos) # Add All button
    time.sleep(0.1)
    
    pa.click(925, 303) # Selected PNR List combo box
    old_rloc = ''
    
    while True:
        data = lib_win.copy()
        rloc = data[:6]
        if rloc == old_rloc: break
        
        old_rloc = rloc
        in_outbound_rlocs.append(rloc)
        pa.press('down')
        time.sleep(0.01)

    print('in_outbound_rlocs = ', in_outbound_rlocs)
    pa.click(1087, 665) # Cancel button to close window Retrieve Passenger List
    time.sleep(0.1)
    #Window "Do you want to save your changes?" open
    pa.press('tab') # No button
    time.sleep(0.01)
    pa.press('enter')
    time.sleep(0.1)
    
    return total_pax_inout_bound, in_outbound_rlocs
'''

def launch_afs():
    #Input: in window Update Default Option or Create Passengers List Option
    #Output: open window Automatic Flight Selection
    
    logStr = 'launch_afs'
    print(logStr)
    logging.warning(logStr)
    
    pa.keyDown('alt'); pa.press('n'); pa.keyUp('alt') # Launch AFS
    #lib_win.wait_until_window_open(AutomaticFlightSelection_win, timeout)
    # Co 2 cua so giong nhau hien ra lan luot!
    cursor.wait_cursor('ARROW', timeout)
    time.sleep(1)
    cursor.wait_cursor('ARROW', timeout)


def get_scrollbar_region():
    #return region to check if it is the top of the scroll bar
    
    start = (782, 291)
    end = (804, 342)
    width = end[0] - start[0]
    height = end[1] - start[1]
    
    return (start[0], start[1], width, height)
    

def get_scrollbar_region2():
    #return region to check if it is the top of the grid
    
    start = (770, 260)
    end = (815, 320)
    width = end[0] - start[0]
    height = end[1] - start[1]
    
    return (start[0], start[1], width, height)
    
    
def move_pax(comp, avail, overbook, in_outbound_rlocs, all_prot_rlocs):
    #In window Retrieve Passenger List
    #Input: comp, avail, overbook, in_outbound_rlocs, all_prot_rlocs
    #Output: move rlocs of compartment comp that not in in_outbound_rlocs to Selected PNR List box
    #   return total_num_pax
    
    logStr = 'move_pax'
    print(logStr)
    logging.warning(logStr)
    
    total_num_pax = 0

    pa.click(760, 217) # Cabin Code box
    time.sleep(0.01)
    pa.press(comp) # C or Y cabin
    pa.keyDown('alt'); pa.press('r'); pa.keyUp('alt') # button Retrieve
    cursor.wait_cursor('ARROW', timeout)

    if pa.locateOnScreen(NoPnrRetrieve_win, grayscale=True, confidence=0.9) is not None:
        pa.press('enter') # OK button to close window
        time.sleep(0.01)
    else: # move rloc to Selected PNR List box
        # Add each rloc:
        pa.click(319, 304) # first cell of Available Passengers List combo box
        time.sleep(0.01)
        #Chọn các PNR theo thứ tự từ dưới lên trên
        pa.keyDown('ctrl'); pa.press('end'); pa.keyUp('ctrl') # move to bottom row
        time.sleep(0.01)

        while avail > 0 and overbook > 0:
            # chi chuyen khach overbook (so voi Default Option) sang flt khac:
            # Cac dong co the giong het nhau vi khach co cung surname
            line = lib_win.copy() # 53MTXV,TEST,C,2,HK,false or 
                                  # WPDLHT,NGUYEN,L,2,HK,true
            arr = line.split(',')
            rloc = arr[0]
            num_pax = int(arr[3])
            #print(f'rloc = {rloc}, num_pax = {num_pax}')
            # flt co du cho de prot pax:
            if (rloc not in in_outbound_rlocs) and (rloc not in all_prot_rlocs) and num_pax <= avail:
                all_prot_rlocs.append(rloc)
                #protected_numpax.append(num_pax)
                print(f'rloc = {rloc}, num_pax = {num_pax}')
                
                pa.keyDown('alt'); pa.press('a'); pa.keyUp('alt') # button Add to move rloc to Selected PNR List
                time.sleep(0.01)
                total_num_pax += num_pax
                avail -= num_pax
                overbook -= num_pax
                #Move focus back to Available Passengers List combo box:
                if avail > 0:
                    pa.click(925, 304) # click to first row of Selected PNR List
                    time.sleep(0.01)
                    for _ in range(4):
                        pa.hotkey('ctrl', 'shift', 'tab')
                        time.sleep(0.01)
                
            if pa.locateOnScreen(end_of_list, region=scrbar_region, grayscale=False, confidence=0.98) is not None or \
               pa.locateOnScreen(end_of_list2, region=scrbar_region2, grayscale=False, confidence=0.98) is not None:
                print(f'line = {line}: end of list')
                break

            #Khong nhay coc theo cach nay duoc vi pax dat extra seat chi co 1 dong! (thieu 1 dong) or
            #group pnr chua co ten khach chi co 1 dong group name
            #Group pnr: ngoai ten khach con co them 1 dong group name (thua 1 dong)
            #pa.press('up', presses = num_pax, interval=0.01) # next above rloc
            
            pa.press('up')
            
    print(f'avail = {avail}, overbook = {overbook}')
    return total_num_pax


def protect_pax_multi_flt(bkg, avail):
    #In window Re-accommodation flt/dptDate.
    
    #Input: 
        # bkg: so khach khoang C va Y cua chuyen bi huy
        # avail: so cho avail khoang C va Y cua chuyen thay the trong default option (first choice)
    #Output:
        #Move overbook pax cua Default Option to multi flt/date
    #Steps:
        #Update Default Option --> launch AFS --> tim flt/date can chuyen khach sang
        #Open window Create Passengers List Option 1
        #Open window Retrieve Passenger List
        #Retrieve Inbound or Outbound Passengers
        #Select PNR List for C pax and Y pax
        #Launch AFS to select flight to move C and Y pax to prot_to_flts
        #Save Passengers List Option 1
        #Commit Re-accommodation
        
    global logStr
    logStr = 'protect_pax_multi_flt'
    print(logStr)
    logging.warning(logStr)
    
    overbook = get_overbook(bkg, avail) # overbook pax cua Default Option
    print('overbook = ', overbook)
    pa.keyDown('alt'); pa.press('u'); pa.keyUp('alt') # button Update...
    lib_win.wait_until_window_open(UpdateDefaultOption_win, timeout)

    launch_afs()

    #Lay danh sach cac chuyen bay co the chuyen khach:
    bOk, prot_to_flts = get_prot_to_flts(overbook)
    print('prot_to_flts = ', prot_to_flts)
    #prot_to_flts: [{'flt': '0229', 'dptDate': '12Jul23', 'avail_C': 26, 'avail_Y': 263}, ]
    
    #Close window Automatic Flight Selection:
    pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl') # move to Cancel button
    time.sleep(0.01)
    pa.press('enter')
    time.sleep(0.01)
    
    #Return to window Update Default Option --> Close it:
    pa.press('esc')
    time.sleep(0.01)
    lib_win.wait_until_window_open(SaveChanges_win, timeout)
    pa.press('tab')
    time.sleep(0.01)
    pa.press('enter') # No button
    time.sleep(0.1)

    #Return to window Re-accommodation flt/dptDate:
    #bOk = True if total_avail_C >= overbook['C'] and total_avail_Y >= overbook['Y']
    if not bOk:
        logStr = 'Prot Failed. Not enough seats available to protect pax!'
        print(logStr)
        logging.warning(logStr)
        
        pa.press('esc') # Cancel button
        cursor.wait_cursor('ARROW', timeout)
        
        pa.keyDown('alt'); pa.press('y'); pa.keyUp('alt') # Yes button to confirm cancel re-acc
        cursor.wait_cursor('ARROW', timeout)
        #Return to window SET
        return bOk # failed

    bFirstProt_ToFlt = True
    in_outbound_rlocs = []
    all_prot_rlocs = []
    total_pax_inout_bound = 0
    bOk = False
    
    while len(prot_to_flts) > 0 and not bOk:
        prot_to = prot_to_flts.pop(0) # get first item
        
        if (overbook['C'] > 0 and prot_to['avail_C'] > 0) or \
           (overbook['Y'] > 0 and prot_to['avail_Y'] > 0):
            print('prot_to = ', prot_to)
            pa.keyDown('alt'); pa.press('x'); pa.keyUp('alt') # button Create PAX List Option
            lib_win.wait_until_window_open(CreatePaxListOption_win, timeout)
            #Window Create Passengers List Option 1 open

            if bFirstProt_ToFlt:
                total_pax_inout_bound, in_outbound_rlocs = get_in_outbound_rlocs() # get pax in_outbound only 1 time
                bFirstProt_ToFlt = False
                
            pa.keyDown('alt'); pa.press('r'); pa.keyUp('alt') # button Retrieve Passenger List
            cursor.wait_cursor('ARROW', timeout)
            #Window Retrieve Passenger List open
            #Move to Passenger List combo box:
            for _ in range(2):
                pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl')
                time.sleep(0.01) 
            pa.press('l', presses=6, interval=0.01) # select List by Cabin
            
            pax_moved_C = pax_moved_Y = 0
            #C pax:
            if overbook['C'] > 0 and prot_to['avail_C'] > 0:
                pax_moved_C = move_pax('C', prot_to['avail_C'], overbook['C'], in_outbound_rlocs, all_prot_rlocs)
                overbook['C'] -= pax_moved_C
                print(f'pax_moved_C = {pax_moved_C}')
            #Y pax:
            if overbook['Y'] > 0 and prot_to['avail_Y'] > 0:
                pax_moved_Y = move_pax('Y', prot_to['avail_Y'], overbook['Y'], in_outbound_rlocs, all_prot_rlocs)
                overbook['Y'] -= pax_moved_Y
                print(f'pax_moved_Y = {pax_moved_Y}')
            #OK button is disabled if no rloc moved!
            if pax_moved_C == 0 and pax_moved_Y == 0:
                print('Cannot move rloc because pnr size > avail seats!')
                exit()
                pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl') # move to View PNR button to close window
                time.sleep(0.01)
                pa.press('esc') # close window Retrieve Passenger List
                time.sleep(0.1)
                
                #Return to window Create Passengers List Option --> close it:
                pa.press('esc')
                time.sleep(0.1)
            else:
                pa.keyDown('alt'); pa.press('o'); pa.keyUp('alt') # OK button to close window Retrieve Passenger List
                cursor.wait_cursor('ARROW', timeout)

                #Return to window Create Passengers List Option --> click Launch AFS button:
                launch_afs()
                
                # In window Automatic Flight Selection
                find_prot_to_flt(prot_to['flt'], prot_to['dptDate'])
                #exit()
                
                pa.keyDown('alt'); pa.press('o'); pa.keyUp('alt') # OK button to close window Automatic Flight Selection
                cursor.wait_cursor('ARROW', timeout)

                if pa.locateOnScreen(SaveOption_win[0], grayscale=True, confidence=0.9) is not None:
                    pa.press('enter')
                    time.sleep(0.1)
                    
                #Return to window Create Passengers List Option --> click Save button:
                pa.keyDown('alt'); pa.press('s'); pa.keyUp('alt') # Save button
                cursor.wait_cursor('ARROW', timeout)
                #Return to window Re-accommodation QH flt/date --> move pax to next flight or Commit
                
                bOk = (overbook['C'] <= 0 and overbook['Y'] <= 0) or overbook['C'] + overbook['Y'] <= total_pax_inout_bound
                
    #Return to window Re-accommodation QH flt/date
    print(f'total_pax_inout_bound ={total_pax_inout_bound}')
    print('overbook =', overbook)
    
    if bOk: #chuyen duoc khach thanh cong:
        print('bOk = ', bOk, 'Commit')
    else: #khong chuyen duoc het khach:
        print('bOk = ', bOk, 'Failed')
    #exit()
    
    if bOk: #chuyen duoc khach thanh cong:
        pa.keyDown('alt'); pa.press('m'); pa.keyUp('alt') # Commit button
        cursor.wait_cursor('ARROW', timeout)
        
        if pa.locateOnScreen(CommitError_win[0], grayscale=True,confidence=0.9) is not None:
            logStr = 'Prot Failed! ' + CommitError_win[3]
            #print(logStr)
            #logging.warning(logStr)
            bOk = False
            #raise Exception(logStr)
        else:
            logStr = 'Prot OK'
    else: #khong chuyen duoc het khach:
        pa.press('esc')
        time.sleep(0.1)
        #A confirmation window open --> Yes
        pa.press('enter')
        cursor.wait_cursor('ARROW', timeout)
        logStr = 'Prot Not OK'
    
    print(logStr)
    logging.warning(logStr)
    #Return to window SET
    return bOk


def get_overbook(bkg, avail):
    #Input: bkg, avail
    #Output: overbook
    
    ovb = {}
    ovb['C'] = max(0, bkg['C'] - avail['C']) # so < 0 thi chuyen thanh 0
    ovb['Y'] = max(0, bkg['Y'] - avail['Y'])

    return ovb


def change_config(r):
    #In window SET
    #Input: flt, dptDate dang date
    #Output: 
        #open window Inventory - QH... : menu Display --> Flight Date Inventory...
        #enter flt/date --> Search to get Config, Aircarft Type, AU, Bkg, GAV

    logStr = 'change_config'
    print(logStr)
    logging.warning(logStr)

    pa.keyDown('alt'); pa.press('2'); pa.keyUp('alt') # menu Inventory Management
    time.sleep(0.01)
    pa.press('enter')
    #cursor.wait_cursor('ARROW', timeout)
    lib_win.wait_until_window_open(SearchFlightDate_win, timeout)
    #window Search Flight Date open
    
    #pa.press('tab') # move to flight number box
    #time.sleep(0.01)
    depDateStr = r.depDate.strftime("%d%b%y")
    pa.write(r.flt)
    time.sleep(0.01)
    pa.press('tab')
    time.sleep(0.01)
    pa.write(depDateStr)
    time.sleep(0.01)
    pa.press('enter')
    cursor.wait_cursor('ARROW', timeout)

    #window Inventory - QH flt/date open
    inven = get_inven(r.flt, r.depDate)
    #print('inven = ', inven)
    
    #Close window Inventory - QH flt/date:
    pa.keyDown('ctrl'); pa.press('f4'); pa.keyUp('ctrl')
    cursor.wait_cursor('ARROW', timeout)

    return inven


'''
def change_config(r):
    #In window SET
    #Input: flt, dptDate dang date, DOW
    #Output: 
        #open window Inventory - QH... : menu Display --> Flight Date Inventory...
        #enter each flt/date --> Search to get Config, Aircarft Type, AU, Bkg, GAV

    logStr = 'change_config'
    print(logStr)
    logging.warning(logStr)

    pa.keyDown('alt'); pa.press('2'); pa.keyUp('alt') # menu Inventory Management
    time.sleep(0.01)
    pa.press('enter')
    #cursor.wait_cursor('ARROW', timeout)
    lib_win.wait_until_window_open(SearchFlightDate_win, timeout)
    #window Search Flight Date open
    
    #pa.press('tab') # move to flight number box
    #time.sleep(0.01)
    depDateStr = r.dptDate.strftime("%d%b%y")
    pa.write(r.flt)
    time.sleep(0.01)
    pa.press('tab')
    time.sleep(0.01)
    pa.write(depDateStr)
    time.sleep(0.01)
    pa.press('enter')
    cursor.wait_cursor('ARROW', timeout)

    #window Inventory - QH flt/date open
    inven = get_inven(r.flt, r.dptDate)
    #print('inven = ', inven)
    r.Result = 'OK'
    r.Reason = ''
    CopyFltToDb(r, inven)
    
    depDate = mylib.add_day2(r.From, 1)
    while depDate <= r.To:
        dow_depDate = depDate.weekday() + 1 # weekday() from 0 (Mon) to 6 (Sun)
        if str(dow_depDate) in r.dow:
            depDateStr = depDate.strftime("%d%b%y")

            pa.click(375, 160) # Flight Date box
            time.sleep(0.01)
            pa.write(depDateStr)
            time.sleep(0.01)
            pa.press('enter')
            cursor.wait_cursor('ARROW', timeout)

            inven = get_inven(r.flt, depDate)
            #print('inven = ', inven)
            CopyFltToDb(r, inven)

        depDate = mylib.add_day2(depDate, 1)

    #Close window Inventory - QH flt/date:
    pa.keyDown('ctrl'); pa.press('f4'); pa.keyUp('ctrl')
    cursor.wait_cursor('ARROW', timeout)

    return True
'''

def get_inven(flt, dptDate):
    #Input: in window Inventory - QH flt dptDate
        # dptDate dang date
    #Output: Config, Aircraft, AU_C, AU_Y, Bkg_C, Bkg_Y, GAV_C, GAV_Y
    
    logStr = 'get_inven'
    print(logStr)
    logging.warning(logStr)
    
    inven = {}
    #dptDate.strftime("%Y-%b-%d")
    pa.click(402, 253)
    data = lib_win.copy()
    inven['Config'] = data # 81818A
    
    pa.press('tab')
    data = lib_win.copy()
    inven['Aircraft'] = data # 787
    
    pa.click(440, 296)
    data = lib_win.copy()
    if data.isnumeric() or data[0]=='-':
        inven['AU_C'] = int(data) # 26
    else:
        raise Exception(f'AU_C: {data} is not a number!')
        
    pa.press('down')
    data = lib_win.copy()
    if data.isnumeric() or data[0]=='-':
        inven['AU_Y'] = int(data) # 268
    else:
        raise Exception(f'AU_Y: {data} is not a number!')
        
    pa.press('up')
    time.sleep(0.01)
    pa.press('tab', presses=7, interval=0.01)
    data = lib_win.copy()
    if data.isnumeric() or data[0]=='-':
        inven['Bkg_C'] = int(data) # 8
    else:
        raise Exception(f'Bkg_C: {data} is not a number!')
    pa.press('down')
    data = lib_win.copy()
    if data.isnumeric() or data[0]=='-':
        inven['Bkg_Y'] = int(data) # 39
    else:
        raise Exception(f'Bkg_Y: {data} is not a number!')
        
    pa.press('up')
    time.sleep(0.01)
    pa.press('tab', presses=5, interval=0.01)
    data = lib_win.copy()
    if data.isnumeric() or data[0]=='-':
        inven['GAV_C'] = int(data) # 18
    else:
        raise Exception(f'GAV_C: {data} is not a number!')
        
    pa.press('down')
    data = lib_win.copy()
    if data.isnumeric() or data[0]=='-':
        inven['GAV_Y'] = int(data) # 229
    else:
        raise Exception(f'GAV_Y: {data} is not a number!')
    return inven


'''
def CopyFltToDb(r, inven):
    #Input: r, inven
    #Output: copy to local MS Access va SQL Server DB flight da run SC

    logStr = 'CopyFltToDb'
    print(logStr)
    logging.warning(logStr)

    r.RunDate = datetime.date.today().strftime("%Y-%b-%d")
    r.RunTime = datetime.datetime.now().strftime("%H:%M:%S")

    #print('r = ', r)
    #Ghi log vao local MS Access va SQL Server DB: da xac dinh env: staging hay production: table tblSkdChg:
    query, query_temp = lib_win.get_log_queries(bStaging)
    
    i = SimpleNamespace(**inven)
    dow = i.dptDate.weekday() + 1
    insert_row = [r.flt, r.org, r.dstn, i.dptDate, i.dptDate, dow, r.SCType, r.SCReason, \
        r.DepTime, r.ArrTime, r.ProtectToFlt, r.ProtectToOrg, r.ProtectToDstn, r.ProtectTo_DC, r.RunDate, r.RunTime, \
        i.Config, i.Aircraft, i.AU_C, i.AU_Y, i.Bkg_C, i.Bkg_Y, i.GAV_C, i.GAV_Y, \
        r.Result, r.Reason]

    lib_win.insert_skdchg_table(query, query_temp, insert_row)
'''

def NoProtect():
    #Cancel flight, No Protect
    #   in window Re-accommodation Solution (after in window SET --> Accept button)
    #Output:
    
    logStr = 'NoProtect'
    print(logStr)
    logging.warning(logStr)
    
    pa.press('tab')
    time.sleep(0.01)
    pa.press('right') # select Manual method
    time.sleep(0.01)
    pa.click(638, 436) # No Alternative
    time.sleep(0.01)
    pa.click(967, 469) #OK button
    #pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl') # move to OK button
    #time.sleep(0.01)
    #pa.press('enter') # OK button
    cursor.wait_cursor('ARROW', timeout)
    #Return to window Re-accommodation QH xxx/ddMMMyy
    
    #Get number of booking:
    pa.click(412, 302) # move to C compartment
    time.sleep(0.01)
    pa.keyDown('ctrl'); pa.press('c'); pa.keyUp('ctrl')
    pax_C = int(cb.paste())
    
    pa.press('tab') # move to Y compartment
    time.sleep(0.01)
    pa.keyDown('ctrl'); pa.press('c'); pa.keyUp('ctrl')
    pax_Y = int(cb.paste())
    
    pa.keyDown('alt'); pa.press('m'); pa.keyUp('alt') #Commit button --> return to SET window
    cursor.wait_cursor('ARROW', timeout)

    return (pax_C, pax_Y)


def ProtectByUser(ProtectToFlt, ProtectToDate, ProtectToOrg, ProtectToDstn):
    #Cancel flight, Protect to user specified flight
    #Input: ProtectToFlt, ProtectToDate, ProtectToOrg, ProtectToDstn
    #   ProtectToDate dang ddMMMyy
    #in window Re-accommodation Solution --> OK (after in window SET --> Accept button)
    #   --> in window Re-accommodation QH xxx/ddMMMyy
    #Output: Chuyen khach sang chuyen bay xac dinh boi user
    #   He thong dang chon Default Option 1 --> Update button
    
    global logStr
    logStr = 'ProtectByUser'
    print(logStr)
    logging.warning(logStr)
    
    pa.keyDown('alt'); pa.press('u'); pa.keyUp('alt') #Update button
    cursor.wait_cursor('ARROW', timeout)
    #Window Update Default Option 1 open
    
    #Move to Proposed Journey, Flight box:
    for _ in range(5):
        pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl')
    
    pa.write(ProtectToFlt, interval=0.01)
    pa.press('tab')
    time.sleep(0.01)
    pa.write(ProtectToDate, interval=0.01)
    pa.press('tab')
    time.sleep(0.01)
    pa.write(ProtectToOrg + ProtectToDstn, interval=0.01)
    pa.keyDown('alt'); pa.press('s'); pa.keyUp('alt') #Save button
    cursor.wait_cursor('ARROW', timeout)
    #Window Update Default Option 1 close
    #In window Re-accommodation QH xxx/ddMMMyy
    
    #menu Tools --> Availability
    bkg, avail = get_availability()
    #print(f'bkg = {bkg}, avail = {avail}')

    # in window Re-accommodation QH flt/dptDate:
    if bkg['C'] + bkg['Y'] == 0 or (bkg['C'] <= avail['C'] and bkg['Y'] <= avail['Y']):
        # chuyến bay khong pax or đủ chỗ:
        pa.keyDown('alt'); pa.press('m'); pa.keyUp('alt') #Commit button --> return to SET window
        cursor.wait_cursor('ARROW', timeout)
        logStr = 'Prot OK' 
        print(logStr)
        logging.warning(logStr)
        bOk = True
    else: # chuyến bay khong đủ chỗ: click Cancel button
        CancelPos = pa.locateOnScreen(ReaccCancelButton, grayscale=True, confidence=0.9)
        pa.click(CancelPos)
        lib_win.wait_until_window_open(CancelRequestedConfirm_win, timeout)
        pa.press('enter') # Yes button
        cursor.wait_cursor('ARROW', timeout)
        
        logStr = f'Prot Failed. Not enough seat'
        print(logStr)
        logging.warning(logStr)
        
        bOk = False
        #return to window SET
    return bOk, bkg, avail


def cancel_flt(ProtectToFlt, ProtectToDate, ProtectToOrg, ProtectToDstn):
    #Input: ProtectToFlt, ProtectToDate, ProtectToOrg, ProtectToDstn
    #   in window Re-accommodation Solution (after in window SET --> Accept button)
    #Output: 
        # Chuyen khach sang chuyen bay khac
    
    global logStr
    logStr = 'cancel_flt'
    print(logStr)
    logging.warning(logStr)

    bkg = {'C': 0, 'Y': 0}
    avail = {'C': 0, 'Y': 0}
    
    if ProtectToFlt == 'NON': #No Protect
        bkg['C'], bkg['Y'] = NoProtect()
        bOk = True
    else:
        bOk = False
        #After click Accept button: window Re-Accommodation Solution open, method Automatic selected
        pa.press('enter') # re-accommodation method: Automatic
        cursor.wait_cursor('ARROW', timeout) 
        
        if pa.locateOnScreen(CancelNoOptionCreated_win[0], grayscale=True, confidence=0.9) is not None:
        #Case 1: No protect to flight:
            pa.keyDown('ctrl'); pa.press('tab'); pa.keyUp('ctrl') # move to Close button
            time.sleep(0.01)
            pa.press('enter')
            time.sleep(0.01)
            CancelPos = pa.locateOnScreen(ReaccCancelButton, grayscale=True, confidence=0.9)
            pa.click(CancelPos)
            
            lib_win.wait_until_window_open(CancelRequestedConfirm_win, timeout)
            pa.press('enter') # Yes button
            cursor.wait_cursor('ARROW', timeout)
            
            logStr = f'Prot Failed. {CancelNoOptionCreated_win[3]}'
            print(logStr)
            logging.warning(logStr)
            return bOk, bkg, avail
        
        if ProtectToFlt != '': # Protect to user specified flight
            bOk, bkg, avail = ProtectByUser(ProtectToFlt, ProtectToDate, ProtectToOrg, ProtectToDstn)
        
        else:
            # Protect using AFS
            # Lay so khach tren chuyen bay bi huy va avail cua Default Option
            #   Chuyen khach sang 1 chuyen bay theo Default Option hay nhieu chuyen bay = cach select pnr
            
            #Case 2: hệ thống tìm được chuyến bay thay thế: window Re-accommodation QH flt/dptDate open
            #menu Tools --> Availability
            bkg, avail = get_availability()
            #print(f'bkg = {bkg}, avail = {avail}')

            # in window Re-accommodation QH flt/dptDate:
            if bkg['C'] + bkg['Y'] == 0 or (bkg['C'] <= avail['C'] and bkg['Y'] <= avail['Y']):
                # chuyến bay khong pax or đủ chỗ:
                pa.keyDown('alt'); pa.press('m'); pa.keyUp('alt') #Commit button --> return to SET window
                cursor.wait_cursor('ARROW', timeout)
                
                if pa.locateOnScreen(CommitError_win[0], grayscale=True,confidence=0.9) is not None:
                    logStr = 'Prot Failed! ' + CommitError_win[3]
                    #raise Exception(logStr)
                else:
                    logStr = 'Prot OK'
                    bOk = True
                    
                print(logStr)
                logging.warning(logStr)
            else:
                bOk = protect_pax_multi_flt(bkg, avail)

    return bOk, bkg, avail


def change_time():
    #Input: in window SET va da nhan Accept button
    #Output: bkg, avail of C, Y
    
    logStr = 'change_time'
    print(logStr)
    logging.warning(logStr)

    #After click Accept button: window Re-Accommodation Solution open, method Automatic selected
    pa.press('tab') # move to Re-accommodation method: Manual
    time.sleep(0.01)
    pa.press('right') # select Manual
    time.sleep(0.01)
    #Default to Same Flight Reacc
    pa.press('enter') # OK button
    cursor.wait_cursor('ARROW', timeout)

    #Get pax C, Y: menu Tools --> Availability
    bkg, avail = get_availability()
    #print(f'bkg = {bkg}, avail = {avail}')
    
    #Commit:
    pa.keyDown('alt'); pa.press('m'); pa.keyUp('alt') #Commit button --> return to SET window
    cursor.wait_cursor('ARROW', timeout)
    logStr = 'change_time OK'
    print(logStr)
    logging.warning(logStr)

    return bkg, avail


def change_time_config(r):
    #Input: in window SET va da nhan Accept button
    #Output: change both time and config
    
    logStr = 'change_time_config'
    print(logStr)
    logging.warning(logStr)
    
    bOk = change_time()
    if bOk:
        bOk = change_config(r)
    return bOk


scrbar_region = get_scrollbar_region()
scrbar_region2 = get_scrollbar_region2()

if __name__ == '__main__':

    flt = '107'
    dptDateFrom = mylib.str2date('11-Jul-2023')
    dptDateTo = mylib.str2date('11-Jul-2023')
    dow = '234567'
    
    pa.click(center_scr)
    change_config(flt, dptDateFrom, dptDateTo, dow)