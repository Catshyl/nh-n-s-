import logging

import mylib
import soap
import sms_api


def send_sms(flt, year, month, day, boardPoint, offPoint, msg):
    #Input: flt, year, month, day, boardPoint, offPoint
    #Output: send sms to all pax in flt/date
    
    mylib.create_log()
    print('send_sms')
    
    rlocs, err_msg, session = soap.ListPax(flt, year, month, day, boardPoint, offPoint)
    if err_msg != '':
        print('Error = ', err_msg)
        return

    for rloc in rlocs:
        print('-' * 10)
        pnr, session, err_msg = soap.PNR_Retrieve(rloc, session)
        if err_msg != '':
            print(err_msg)
        else:
            print(pnr)
            
            '''
            tel = ''
            for contact in pnr['contacts']:
                if contact['type'] == 'phone': # phone or email
                    tel = contact['data']
                    break
                    
            if tel != '':
                print(f'{rloc} : {tel}')
                bOk, err_msg = sms_api.SendSms(tel, msg)
                if not bOk:
                    print(err_msg)
            '''
    logging.shutdown() # close log text file


if __name__ == '__main__':

    flt  = '216'
    year, month, day = 2023, 10, 13
    boardPoint, offPoint = 'HAN', 'SGN'
    msg = f'SC for QH{flt} on {day}{month}{year}'
    
    send_sms(flt, year, month, day, boardPoint, offPoint, msg)
    
    #5SCRHO 5SCH3A 5SD24Y