import requests
import time
import logging

#import mylib
api_url = "http://125.212.226.79:9020/service/sms_api/"
username = 'bamboo'
password = 'bamboo#Jsd02!'

requests.adapters.DEFAULT_RETRIES = 5 # increase retries number

Viettel_Tel = ['86', '96', '97', '98']
Vinaphone_Tel = ['81', '82', '83', '84', '85', '91', '94']
Mobifone_Tel = ['70', '76', '77', '78', '79', '89', '90', '93']
Vietnamobile_Tel = ['52', '56', '58', '92']
GMobile_Tel = ['59', '99']
Itelecom_Tel = ['87'] # Indochina Telecom
Reddi_Tel = ['55']
    

def get_telcoCode(tel_num):
    #Input: tel_num (khong co country code - 84 o dau), dang 983830466 / 0983830466
    #Output: telcoCode : ma nha mang
    '''
        VTE: Mã code của mạng Viettel
        GPC: Mã code của mạng Vinaphone
        VMS: Mã code của mạng Mobifone
        VNM: mã code của mạng Vietnamobile
        BL: Mã code của mạng GMobile
        DDG: Mã code của mạng Itelecom
        RDD: Mã code mạng Reddi
    '''
    
    if tel_num[0] == '0': tel_num = tel_num[1:]
    first_char = tel_num[:1]
    first_2_chars = tel_num[:2]
    
    #https://en.wikipedia.org/wiki/Telephone_numbers_in_Vietnam
    telcoCode = ''
    if first_char == '3' or first_2_chars in Viettel_Tel:
        telcoCode = 'VTE' # Viettel
    elif first_2_chars in Vinaphone_Tel:
        telcoCode = 'GPC' # Vinaphone
    elif first_2_chars in Mobifone_Tel:
        telcoCode = 'VMS' # Mobifone
    elif first_2_chars in Vietnamobile_Tel:
        telcoCode = 'VNM' # Vietnamobile
    elif first_2_chars in GMobile_Tel:
        telcoCode = 'BL' # GMobile
    elif first_2_chars in Itelecom_Tel:
        telcoCode = 'DDG' # Itelecom
    elif first_2_chars in Reddi_Tel:
        telcoCode = 'RDD' # Reddi
    else:
        raise Exception(f'Unsupported Telecom Operator. tel_num = {tel_num}')
        
    return telcoCode
    

def SendSms(phone_num, msg):
    #Input: phone_num, msg
    #Output: send msg to phone_num
    
    logStr = 'SendSms'
    print(logStr)
    logging.warning(logStr)
    
    tel_country_code = '84'
    if phone_num[:2] == tel_country_code: # bo country code
        phone_num = phone_num[2:]
        
    if len(phone_num) < 9:
        return False, 'Invalid phone number!'
        
    try:
        telcoCode = get_telcoCode(phone_num)
        
        request_data = {
              "phone": phone_num,
              "mess": msg,
              "user": username,
              "pass": password,
              "tranId": "",
              "brandName": "HK BAMBOO",
              "dataEncode": 0,
              "sendTime": "",
              "telcoCode": telcoCode
            }
        
        response = ''
        err_msg = ''
        while response == '':
            try:
                # https://linuxpip.org/fix-max-retries-exceeded-with-url-error-python/
                s = requests.session()
                s.keep_alive = False # disable keep alive
                # make the service call:
                #response = requests.post(api_url, json = request_data, timeout=None) # wait forever for a response # stream=True,
                response = s.post(api_url, json = request_data, verify=False, timeout=None)
                #print('response = ' , response) # <Response [200]>
                
                response_obj = response.json()
                logStr = f'response_obj = {response_obj}'
                print(logStr)
                logging.warning(logStr)
                #print('status_code = ', response.status_code) # 200
                #print('reason = ', response.reason)
                #response_obj =  {'code': 1, 'message': 'Success', 'transId': '840396455052-d7c65fa8c2d9a3', 'oper': 'VTE', 'totalSMS': 1}
                #response_obj =  {'code': 15, 'message': 'The Same Content Short Time', 'transId': '840396455052-d7cb286ae17476', 'oper': 'VTE', 'totalSMS': 1}
                if response_obj['code'] == 1:
                    bOK = True
                else:
                    bOK = False
                    err_msg = response_obj['message']
                    
            except requests.exceptions.ConnectionError as ex:
                print("Connection refused by the server..")
                print("Let me sleep for 10 seconds")
                print("ZZzzzz...")
                time.sleep(10)
                print("Was a nice sleep, now let me continue...")
                continue
                #TimeoutError: [WinError 10060] A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond
                
            except Exception as ex:
                bOK = False
                err_msg = str(ex)

    except Exception as ex:
        bOK = False
        err_msg = str(ex)
        
    return bOK, err_msg


if __name__ == '__main__':
    phone_num = '84396455052' 
    #telcoCode = 'VTE' 
    msg = 'Hello LongTD. Msg sent from API with try and SO'
    
    bOk, err_msg = SendSms(phone_num, msg)
    if not bOk:
        print(err_msg)
