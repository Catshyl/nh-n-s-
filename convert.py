from types import SimpleNamespace
import pandas as pd
import logging

import lib_win
import mylib


def readExcel_KHDB(fullFileName):
    logStr = 'readExcel_KHDB'
    print(logStr)
    logging.warning(logStr)
        
    dtype = {'FLT NBR':str, 'Board Point': str, 'Off Point': str, 'DOW': str,
             'New ETD (LT)': str, 'New ETA (LT)': str, 'New CFG': str, 'TAIL #': str, 'Change code':str,
             'Reason':str, 'ServiceType':str}
        
    # Read first sheet:
    df = pd.read_excel(fullFileName, sheet_name=0, parse_dates=['From', 'To'], dtype=dtype)
    df['line_num'] = df.index.values+2
    
    # Bo het dau space, enter:
    df['FLT NBR'] = df['FLT NBR'].str.strip()
    df['FLT NBR'] = df['FLT NBR'].str[2:] # bo QH o dau
    df['Board Point'] = df['Board Point'].str.strip()
    df['Off Point'] = df['Off Point'].str.strip()
    
    df['New ETD (LT)'].fillna('', inplace=True)
    df['New ETD (LT)'] = df['New ETD (LT)'].str.strip() # bo het dau space, enter
    df['New ETD (LT)'] = df['New ETD (LT)'].str[:5]
    df['New ETD (LT)'] = df['New ETD (LT)'].map(lambda x: '0'+x if len(x) == 4 else x)

    df['New ETA (LT)'].fillna('', inplace=True)
    df['New ETA (LT)'] = df['New ETA (LT)'].str.strip() # bo het dau space, enter
    df['New ETA (LT)'] = df['New ETA (LT)'].str[:5]
    df['New ETA (LT)'] = df['New ETA (LT)'].map(lambda x: '0'+x if len(x) == 4 else x)

    
    df['New CFG'] = df['New CFG'].str.strip()
    df['TAIL #'] = df['TAIL #'].str.strip()
    df['Change code'] = df['Change code'].str.strip()

    df.DOW = df.DOW.str.replace(r'[. …]', '', regex=True) # ma unicode 8230 (ellipse)
    df.Reason = df.Reason.str.strip()
    
    df.ProtectTo_DC.fillna(0, inplace=True) 
    df.ProtectTo_DC = df.ProtectTo_DC.astype(int)
    df_acv = lib_win.read_acv_file(False) # file ACV.xlsx
    #print(df_acv)
    df = df.merge(df_acv, left_on=['TAIL #', 'New CFG'], right_on=['RegNum', 'FitConfig'], how='left')
    
    #df.drop(columns=['TAIL #', 'New CFG'], inplace=True)
    # Rename columns:
    columnMaps = {'FLT NBR': 'flt',  'Board Point': 'org', 'Off Point': 'dstn',
                  'New ETD (LT)': 'depTime', 'New ETA (LT)': 'arrTime', 
                  'Change code': 'SCType', 'Reason': 'SCReason', 'IFA': 'dc'}
    df = df.rename(columns=columnMaps)
    
    df.depTime = df.depTime.str.replace(':', '')
    df.arrTime = df.arrTime.str.replace(':', '')
    
    no_acv_df = df[(df['SCType'] == 'CON') & (df['FitConfig'].isnull())]
    if len(no_acv_df) > 0:
        logStr = 'Flights do not ACV table'
        print(logStr)
        #print(no_acv_df)
        print(no_acv_df[['flt', 'org', 'dstn', 'From', 'To', 'DOW', 'TAIL #', 'New CFG', 'line_num']])
        raise Exception(logStr)
    
    df.fillna('', inplace=True) # neu change TIM or CNL thi khong co thong tin ACV
    df.loc[df["SCType"] == "CON", "SCType"] = 'EQT' # replace CON with EQT
    #print('df = ')
    #print(df)
    return df


def get_config(FitConfig):
    #Input: FitConfig dang '26/0/268'
    #Output: 'C8Y162'
    #print('FitConfig = ', FitConfig)
    arr = FitConfig.split('/')
    return f'C{arr[0]}Y{arr[-1]}'
    
    
def convert_row(r, fh):
    #Input: r, fh
    #Output: Convert các chuyến bay trong file input thành định dạng ASM/SSM
        #if MsgType = A --> ASM
        #ele            --> SSM
        #CON --> SSM : them ACV code sau .VV
        #TIM --> SSM
        #CNL --> SSM -->de khi xu ly trong SET window thi se chuyen khach tung flt/date
        
    '''
    SSM
    LT
    NEW XASM
    QH174
    09JUN23 14JUN23 135
    J 320 C8Y168 .VV596
    HAN0935 SGN1055
    //
    SSM
    LT
    EQT
    QH229
    11JUN23 18JUN23 1234567
    J 320 C8Y162.VV582
    SGN/HAN
    //
    SSM
    LT
    TIM
    QH222
    01JUL23 10JUL23 1234567
    HAN1010 SGN1140
    //
    SSM
    LT
    CNL
    QH1413
    02Oct23 02Oct23 1

    ASM
    LT
    TIM
    QH304/10OCT23
    SIN1700 HAN1900
    '''
    
    num_char = 0
    lines = []
    if len(r.flt) == 2: r.flt = '0' + r.flt
    
    # content luu noi dung cua 1 dien
    if r.MsgType == 'A': # ASM: split date range to each date:
        depDate = r.From
        while depDate <= r.To:
            dow_depDate = depDate.weekday() + 1 # dow from 0 (Monday) to 6 (Sunday)
            #print('dow = ', dow, 'dow_depDate = ', dow_depDate)
            if str(dow_depDate) in r.DOW:
                content = f'''{r.SCType}
QH{r.flt}/{mylib.date2str2(depDate)}'''
                if r.SCType == 'EQT':
                    content += f'''
{r.ServiceType} {r.EquipmentType} {get_config(r.FitConfig)}.VV{r.AcvCode}
{r.org}/{r.dstn}'''
                elif r.SCType == 'TIM':
                    ProtectTo_DC = '' if r.ProtectTo_DC == 0 else rf'/{r.ProtectTo_DC}'
                    content += f'''
{r.org}{r.depTime} {r.dstn}{r.arrTime}{ProtectTo_DC}'''

                content += f'''
//
'''
                fh.write(content)
                lines.append(content)
                num_char += len(content)
            depDate = mylib.add_day2(depDate, 1)

    else: # SSM:
        if r.SCType == 'NEW':
            content = f'''NEW XASM
QH{r.flt}
{mylib.date2str2(r.From)} {mylib.date2str2(r.To)} {r.DOW}
{r.ServiceType} {r.EquipmentType} {get_config(r.FitConfig)} .VV{r.AcvCode}
{r.org}{r.depTime} {r.dstn}{r.arrTime}
//
'''
        elif r.SCType == 'EQT' or r.SCType == 'TIM':
            content = f'''{r.SCType}
QH{r.flt}
{mylib.date2str2(r.From)} {mylib.date2str2(r.To)} {r.DOW}'''

            if r.SCType == 'EQT':
                content += f'''
{r.ServiceType} {r.EquipmentType} {get_config(r.FitConfig)}.VV{r.AcvCode}
{r.org}/{r.dstn}
//
'''
            else:
                ProtectTo_DC = '' if r.ProtectTo_DC == 0 else rf'/{r.ProtectTo_DC}'
                content += f'''
{r.org}{r.depTime} {r.dstn}{r.arrTime}{ProtectTo_DC}
//
'''
        elif r.SCType == 'CNL': # dien Cancel : tach giai doan thanh tung ngay:
            depDate = r.From
            while depDate <= r.To:
                dow_depDate = depDate.weekday() + 1 # dow from 0 (Monday) to 6 (Sunday)
                #print('dow = ', dow, 'dow_depDate = ', dow_depDate)
                if str(dow_depDate) in r.DOW:
                    content = f'''CNL
QH{r.flt}
{mylib.date2str2(depDate)} {mylib.date2str2(depDate)} {dow_depDate}
//
'''
                    fh.write(content)
                    lines.append(content)
                    num_char += len(content)
                depDate = mylib.add_day2(depDate, 1)

        if r.SCType != 'CNL':
            fh.write(content)
            lines.append(content)
            num_char = len(content)

    return lines, num_char


def convert_file(fullFileName):
    #Input: fullFileName chua file excel input SC
    #Output: text file chua cac dien ASM/SSM
    
    mylib.create_log() # open log text file
    
    logStr = 'convert_file'
    print(logStr)
    logging.warning(logStr)
    
    outFileName = 'C:/Temp/asm.txt'
    
    df = readExcel_KHDB(fullFileName)
    asm_df = df[df.MsgType == 'A']
    asm_rows = asm_df.to_dict('records') # fastest
    
    ssm_df = df[df.MsgType != 'A']
    ssm_rows = ssm_df.to_dict('records')

    #Convert ASM msg:
    asm_msgs = []
    header = '''ASM
LT
'''
    with open(outFileName, 'w') as fh:
        fh.write(header)
        for row in asm_rows:
            r = SimpleNamespace(**row)
            #print(r)
            lines, _ = convert_row(r, fh)
            asm_msgs.extend(lines)

    asm_msgList = split_msgs(asm_msgs)
    
    #Convert SSM msg:
    ssm_msgs = []
    header = '''SSM
LT
'''
    with open(outFileName, 'a') as fh:
        fh.write('\n' + '=' *10 + '\n')
        fh.write(header)
        for row in ssm_rows:
            r = SimpleNamespace(**row)
            #print(r)
            lines, _ = convert_row(r, fh)
            ssm_msgs.extend(lines)

    ssm_msgList = split_msgs(ssm_msgs)
    
    #print('asm_msgList = ')
    #print(asm_msgList)
    #print('ssm_msgList = ')
    #print(ssm_msgList)
    
    logStr = 'Convert Finished'
    print(logStr)
    logging.warning(logStr)
    logging.shutdown() # close log text file
    
    return outFileName, asm_msgList, ssm_msgList


def split_msgs(msgs):
    #Input: msgs
    #Output: split msgs thanh cac dien nho hon 3500 chars
    
    logStr = 'split_msgs'
    print(logStr)
    logging.warning(logStr)
    
    MAX_CHAR = 1500
    
    msgList = []
    msgItem = [] # msgItem la 1 element trong msgList: tach cac dien trong msgs thanh nhieu msgItem
    total_char = 0 # tong so char trong msgItem
    
    for msg in msgs:
        #print('msg = ', msg)
        num_char = len(msg)
        if total_char + num_char < MAX_CHAR:
            msgItem.append(msg)
            total_char += num_char
        else:
            #print('msgItem = ')
            #print(msgItem)
            msgList.append(msgItem)
            
            msgItem = []
            msgItem.append(msg)
            total_char = num_char
            
    msgList.append(msgItem)

    return msgList


def get_msg_len(msg):
    #Input: msg: a list of string
    #Output: len of msg
    
    size = 0
    for line in msg:
        size += len(line)
        
    return size


if __name__ == '__main__':
    fullFileName = 'E:/MyProg/Python/SkdChg1A_Set/Input.xlsx'
    
    outFileName, asm_msgList, ssm_msgList = convert_file(fullFileName)
    
    for i, msg in enumerate(asm_msgList):
        print(f'len of msg {i} = ', get_msg_len(msg))
        
    for i, msg in enumerate(ssm_msgList):
        print(f'len of msg {i} = ', get_msg_len(msg))