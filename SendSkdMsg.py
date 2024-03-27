import time
import pyautogui as pa
import logging
import clipboard

import cursor
import config

timeout = 60 # seconds

OrgAddr = 'HANASQH'
DestAddrStaging = 'QLGUSQH'
DestAddrProduction = 'MUCSCQH'

def Send(msgType, msgList):
    #Input: msgType, msgList
    #Output: gửi điện SSM/ASM tren 1A Inventory GUI bằng menu Tools --> Teletype
    
    header = f'''{msgType}
LT
'''
    for msg in msgList:
        text = header + ''.join(msg)[0:-4] #bo 2 chars // o cuoi va ky tu xuong dong
        #print('text =\n','='*10,'\n',text)
        clipboard.copy(text)
        pa.keyDown('ctrl'); pa.press('v'); pa.keyUp('ctrl') # paste to 1A Text box
        time.sleep(1)

        pa.keyDown('alt'); pa.press('s'); pa.keyUp('alt') # Send button
        cursor.wait_cursor('ARROW', timeout)
        time.sleep(1)
        pa.press('enter') # OK button
        time.sleep(1)
        pa.press('tab', presses=4, interval=0.1) # move to Text box (content)
        time.sleep(0.1)
        pa.press('delete') # xoa noi dung cu
        time.sleep(0.1)

        if config.bStop: break


def SendSkd(bStaging, asm_msgList, ssm_msgList):
    #Input: bStaging, asm_msgList, ssm_msgList
    #Output: gửi điện SSM/ASM tren 1A Inventory GUI bằng menu Tools --> Teletype
    
    logStr = 'SendSkd'
    print(logStr)
    logging.warning(logStr)
    
    DestAddr = DestAddrStaging if bStaging else DestAddrProduction

    #Click vao ung dung Inventory cua 1A:
    pa.click(config.window_title_pos)

    pa.keyDown('alt'); pa.press('t'); pa.keyUp('alt') # menu Tools
    pa.press('t') # window Teletype open
    cursor.wait_cursor('ARROW', timeout)
    
    pa.press('tab') # move to Origin address box
    time.sleep(0.01)
    pa.write(OrgAddr, interval=0.01)
    time.sleep(0.01)
    pa.press('tab') # move to Destination address box
    time.sleep(0.01)
    pa.write(DestAddr, interval=0.01)
    time.sleep(0.01)
    pa.press('tab') #move to Text box
    time.sleep(0.01)

    if len(asm_msgList[0]) > 0:
        msgType = 'ASM'
        Send(msgType, asm_msgList)
    
    if len(ssm_msgList[0]) > 0:
        msgType = 'SSM'
        Send(msgType, ssm_msgList)
    
