import datetime
import random
import hashlib
import base64

import requests
import xml.etree.ElementTree as ET

import logging

import pnr_class
import pnr_segment


# para for Production, List pax:
WURI = 'https://nodeA3.production.webservices.amadeus.com'
WSAP = '1ASIWMELQH' # if this is wrong  --> error: 17|Session|No agreement on destination
LSSUser = 'WSQHCAT'
password = 'CatKiss@321!'
LSSOfficeId = 'HANQH08CT'


# para for Production, RT PNR:
WSAP = '1ASIWBOCQH'
LSSUser  = 'WSQHBOC'
password = 'BavBoc@2023'
LSSOfficeId = 'HANQH08BO'


# para for UAT, SMS:
WURI = 'https://nodea3.test.webservices.amadeus.com'
WSAP = '1ASIWSMSQHU'
LSSUser = 'WSQHSMS'
password = 'EmailSms@12345'
LSSOfficeId = 'HANQH08ES'

# para for Q, RT PNR, Avail:
'''
WURI = 'https://nodea3.test.webservices.amadeus.com'
WSAP = '1ASIWGENQHU' # if this is wrong  --> error: 17|Session|No agreement on destination
LSSUser = 'WSQHGEN'
password = 'Amadeus@23'
LSSOfficeId = 'HANQH08AA'
'''

# para for Cryptic:
#WSAP = '1ASIWB2BQHU'

# para for Inv_AdvancedGetFlightData:
'''
WSAP = '1ASIWAMSQHU'
LSSUser = 'WSQHAIMS'
password = 'Aims@12345'
LSSOfficeId = 'HANQH08O3'
'''

url = WURI  + '/' + WSAP
LSSOrg = 'QH'

#https://thejpanda.com/2022/01/31/automation-making-a-soap-api-call-in-python-using-a-session-key/

def toBase64(inputBytes):
    return base64.b64encode(inputBytes).decode('ascii') #CryptoJS.enc.Base64.stringify(inputBytes)


def toBytes(inputString):
    #return bytes(inputString, 'ascii')
    return bytes(inputString, 'utf-8') # CryptoJS.enc.Utf8.parse(inputString)
    

def generateRandomString(str_len):
    #Input: str_len
    #Output: string has str_len chars
    
    text = ''
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    for i in range(str_len):
        text += possible[random.randrange(len(possible))]
    return text


def saltPassword(nonce, timestamp, password):
    #https://gist.github.com/daragh/579458cd966e415d0e325b43007ce439
    #https://docs.python.org/3/library/hashlib.html
    #sha1 = CryptoJS.algo.SHA1.create()
    sha1 = hashlib.sha1()
    print("nonce = ", nonce)
    print("timestamp = ", timestamp)
    print("password = ", password)
    
    #sha1Pass = CryptoJS.SHA1(password)
    hash_object = hashlib.sha1(toBytes(password))
    sha1Pass = hash_object.digest()
    print("sha1Pass = ", sha1Pass) # 20 bytes

    sha1.update(toBytes(nonce))
    
    sha1.update(toBytes(timestamp))

    sha1.update(sha1Pass)

    #result = toBase64(sha1.finalize())
    result = toBase64(sha1.digest())
    print("saltPassword = ", result)

    return result


def generate_uniqueID():
    uniqueIDValue = generateRandomString(16) # 16 bytes
    result = toBase64(toBytes(uniqueIDValue)) # 24 bytes
    #print("generate_uniqueID = ", result)

    return result


'''
def generate_messageID() {	
	def random = SecureRandom.getInstance("SHA1PRNG");
	random.setSeed(System.currentTimeMillis());
	def messageIDValue = new byte[16];
	random.nextBytes(messageIDValue);
	return Base64.encode(messageIDValue);
}

def generate_uniqueID() {	
	def random = SecureRandom.getInstance("SHA1PRNG");
	random.setSeed(System.currentTimeMillis());
	def uniqueIDValue = new byte[16];
	random.nextBytes(uniqueIDValue);
	return Base64.encode(uniqueIDValue);
}
'''

def getError(xml):
    #Input: xml
    #Output: error string
    
    root = ET.fromstring(xml)
    msg = root.find(".//faultcode").text
    msg += '-' + root.find(".//faultstring").text.strip()
    return msg
    

def getRequest(SOAPAction, body, bStartSession = False):
    #Input: SOAPAction, body
    #Output: full xml of request
    # Not use Session
    
    SOAPActionEle = '' if SOAPAction == '' else f'<wsa:Action>{SOAPAction}</wsa:Action>'
    
    if bStartSession:
        session_str = '<ses:Session TransactionStatusCode="Start"></ses:Session>'
    else:
        session_str = ''
        
    xml = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sec="http://xml.amadeus.com/2010/06/Security_v1" xmlns:link="http://wsdl.amadeus.com/2010/06/ws/Link_v1" xmlns:ses="http://xml.amadeus.com/2010/06/Session_v3">
    <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:typ="http://xml.amadeus.com/2010/06/Types_v1" xmlns:iat="http://www.iata.org/IATA/2007/00/IATA2010.1">
        <sec:AMA_SecurityHostedUser>
            <sec:UserID POS_Type="1" RequestorType="U" PseudoCityCode="{LSSOfficeId}" AgentDutyCode="SU">
                <typ:RequestorID>
                    <iat:CompanyName>{LSSOrg}</iat:CompanyName>
                </typ:RequestorID>
            </sec:UserID>
        </sec:AMA_SecurityHostedUser>
        <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
            <wsse:UsernameToken>
                <wsse:Username>{LSSUser}</wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">{saltedLSSPass}</wsse:Password>
                <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">{nonceBase64}</wsse:Nonce>
                <wsu:Created>{timestamp}</wsu:Created>
            </wsse:UsernameToken>
        </wsse:Security>
        <wsa:To>{WURI}/{WSAP}</wsa:To>
        {SOAPActionEle}
        <wsa:MessageID>urn:uuid:{generate_uniqueID()}</wsa:MessageID>
        <link:TransactionFlowLink>
            <link:Consumer>
                <link:UniqueID>{uniqueID}</link:UniqueID>
            </link:Consumer>
        </link:TransactionFlowLink>
        {session_str}
    </soapenv:Header>
    <soapenv:Body>
    {body}
    </soapenv:Body>
</soapenv:Envelope>"""

    #The Session o cuoi soapenv:Header   :   <ses:Session TransactionStatusCode="Start"></ses:Session>

    return xml


def getRequestBySession(SOAPAction, body, session, TransactionStatusCode):
    #Input: SOAPAction, body, session, TransactionStatusCode : InSeries/End
    #Output: full xml of request

    if session == None:
        session_str = '<ses:Session TransactionStatusCode="Start"></ses:Session>'
    else:
        session_str = f'''<ses:Session TransactionStatusCode="{TransactionStatusCode}">
        <ses:SessionId>{session['SessionId']}</ses:SessionId>
        <ses:SequenceNumber>{session['SeqNumber']+1}</ses:SequenceNumber>
        <ses:SecurityToken>{session['Token']}</ses:SecurityToken>
      </ses:Session>'''
        
    xml = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sec="http://xml.amadeus.com/2010/06/Security_v1" xmlns:typ="http://xml.amadeus.com/2010/06/Types_v1" xmlns:iat="http://www.iata.org/IATA/2007/00/IATA2010.1" xmlns:app="http://xml.amadeus.com/2010/06/AppMdw_CommonTypes_v3" xmlns:link="http://wsdl.amadeus.com/2010/06/ws/Link_v1" xmlns:ses="http://xml.amadeus.com/2010/06/Session_v3" xmlns:hsf="http://xml.amadeus.com/HSFREQ_07_3_1A">
   <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
      <wsa:To soapenv:mustUnderstand="1">{WURI}/{WSAP}</wsa:To>
      <wsa:Action soapenv:mustUnderstand="1">{SOAPAction}</wsa:Action>
      <wsa:MessageID soapenv:mustUnderstand="1">uuid:{generate_uniqueID()}</wsa:MessageID>
      {session_str}
   </soapenv:Header>
   <soapenv:Body>
      {body}
   </soapenv:Body>
</soapenv:Envelope>"""

    #session['SeqNumber'] += 1
    return xml


def display_ticket():
    print('display_ticket')
    SOAPAction = 'http://webservices.amadeus.com/TKTREQ_04_1_IA'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    #message function 131 for Single Display
    #message function 137 for History Display
    body = f"""<Ticket_ProcessETicket>
        <msgActionDetails>
            <messageFunctionDetails>
                <messageFunction>131</messageFunction>
            </messageFunctionDetails>
        </msgActionDetails>
        <ticketInfoGroup>
            <ticket>
                <documentDetails>
                    <number>9262410000102</number>
                </documentDetails>
            </ticket>
        </ticketInfoGroup>
    </Ticket_ProcessETicket>"""
    
    '''
    body = f"""<Ticket_ProcessEDoc>
            <msgActionDetails>
                <messageFunctionDetails>
                    <messageFunction>131</messageFunction>
                </messageFunctionDetails>
            </msgActionDetails>
            <referenceInfo>
                <reservation>
                    <companyId>QH</companyId>
                    <controlNumber>5OFWK3</controlNumber>
                    <controlType>1</controlType>
                </reservation>
            </referenceInfo>
            <infoGroup>
                <docInfo>
                    <documentDetails>
                        <number>926</number>
                    </documentDetails>
                </docInfo>
            </infoGroup>
        </Ticket_ProcessEDoc>"""
    '''
    xmlRequest = getRequest(SOAPAction, body)
    print(xmlRequest)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    
def GetRlocInQueue(root):
    print('GetRlocInQueue')
    rloc = root.find('.//reservation/controlNumber') # pnrRecLocator
    
    if rloc != None:
        rloc = rloc.text.strip()
    else:
        rloc = '' # neu het item thi queue khong con rloc
        #raise Exception('Cannot find rloc!')
    return rloc


def Queue_PlacePNR(Rloc, QOffice, QNum, QCategory):
    print('Queue_PlacePNR')
    SOAPAction = 'http://webservices.amadeus.com/QUQPCQ_03_1_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<Queue_PlacePNR>
      <placementOption>
        <selectionDetails>
          <option>QEQ</option>
        </selectionDetails>
      </placementOption>
      <targetDetails>
        <targetOffice>
          <sourceType>
            <sourceQualifier1>3</sourceQualifier1>
          </sourceType>
          <originatorDetails>
            <inHouseIdentification1>{QOffice}</inHouseIdentification1>
          </originatorDetails>
        </targetOffice>
        <queueNumber>
          <queueDetails>
            <number>{QNum}</number>
          </queueDetails>
        </queueNumber>
        <categoryDetails>
          <subQueueInfoDetails>
            <identificationType>C</identificationType>
            <itemNumber>{QCategory}</itemNumber>
          </subQueueInfoDetails>
        </categoryDetails>
      </targetDetails>
      <recordLocator>
        <reservation>
          <controlNumber>{Rloc}</controlNumber>
        </reservation>
      </recordLocator>
    </Queue_PlacePNR>"""
    
    xmlRequest = getRequest(SOAPAction, body)
    print(xmlRequest)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    response_xml = response_xml.replace(' xmlns="http://xml.amadeus.com/QUQPCR_03_1_1A"', '')
    root = ET.fromstring(response_xml)
    rloc = GetRlocInQueue(root)
    return rloc


def StartQueue(QOffice, QNum, QCategory):
    print('StartQueue')
    SOAPAction = 'http://webservices.amadeus.com/QUEREQ_09_1_IA'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<QueueMode_ProcessQueue>
        <messageActionDetails>
            <messageFunctionDetails>
                <messageFunction>211</messageFunction>
            </messageFunctionDetails>
        </messageActionDetails>
        <queueInfoDetails>
            <selectionInfoDetails>
                <selectionDetails>
                    <option>QP</option>
                </selectionDetails>
            </selectionInfoDetails>
            <queueGroup>
                <queueInfo>
                    <queueDetails>
                        <number>{QNum}</number>
                    </queueDetails>
                </queueInfo>
                <subQueueInfo>
                    <subQueueInfoDetails>
                        <identificationType>C</identificationType>
                        <itemNumber>{QCategory}</itemNumber>
                    </subQueueInfoDetails>
                </subQueueInfo>
                <subQueueInfo>
                    <subQueueInfoDetails>
                        <identificationType>1</identificationType>
                    </subQueueInfoDetails>
                </subQueueInfo>
                <targetOffice>
                    <internalIdDetails>
                        <inhouseId>{QOffice}</inhouseId>
                    </internalIdDetails>
                </targetOffice>
            </queueGroup>
        </queueInfoDetails>
    </QueueMode_ProcessQueue>"""
    
    xmlRequest = getRequest(SOAPAction, body, True) # start session
    print(xmlRequest)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    response_xml = response_xml.replace(' xmlns="http://xml.amadeus.com/QUERES_09_1_IA"', '')
    root = ET.fromstring(response_xml)
    rloc = GetRlocInQueue(root)
    session = get_session(root)
    
    print('rloc = ', rloc)
    return rloc, session


def IgnoreQueue(rloc, session):
    #Input: rloc, session
    #Output: Remove Queue Item
    #session = {'SessionId': '01RKRLSYMA', 'SeqNumber': 1, 'Token': 'BBNJ90RXU4OA2Y7AIQLHGJCDM'}
    
    print('IgnoreQueue')
    SOAPAction = 'http://webservices.amadeus.com/QUEREQ_09_1_IA'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<QueueMode_ProcessQueue>
        <messageActionDetails>
            <messageFunctionDetails>
                <messageFunction>218</messageFunction>
            </messageFunctionDetails>
        </messageActionDetails>
        <recordLocator>
            <reservation>
                <controlNumber>{rloc}</controlNumber>
            </reservation>
        </recordLocator>
        <queueInfoDetails>
            <selectionInfoDetails>
                <selectionDetails>
                    <option>QP</option>
                </selectionDetails>
            </selectionInfoDetails>
        </queueInfoDetails>
    </QueueMode_ProcessQueue>"""
    
    TransactionStatusCode = 'InSeries'
    xmlRequest = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    print(xmlRequest)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    response_xml = response_xml.replace(' xmlns="http://xml.amadeus.com/QUERES_09_1_IA"', '')
    root = ET.fromstring(response_xml)
    rloc = GetRlocInQueue(root)
    session = get_session(root)
    
    print('rloc = ', rloc)
    return rloc, session


def RemoveQueue(rloc, session):
    #Input: rloc, session
    #Output: Remove Queue Item
    #session = {'SessionId': '01RKRLSYMA', 'SeqNumber': 1, 'Token': 'BBNJ90RXU4OA2Y7AIQLHGJCDM'}
    
    print('RemoveQueue')
    SOAPAction = 'http://webservices.amadeus.com/QUEREQ_09_1_IA'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<QueueMode_ProcessQueue>
        <messageActionDetails>
            <messageFunctionDetails>
                <messageFunction>217</messageFunction>
            </messageFunctionDetails>
        </messageActionDetails>
        <recordLocator>
            <reservation>
                <controlNumber>{rloc}</controlNumber>
            </reservation>
        </recordLocator>
        <queueInfoDetails>
            <selectionInfoDetails>
                <selectionDetails>
                    <option>QP</option>
                </selectionDetails>
            </selectionInfoDetails>
        </queueInfoDetails>
    </QueueMode_ProcessQueue>"""
    
    TransactionStatusCode = 'InSeries'
    xmlRequest = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    print(xmlRequest)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    response_xml = response_xml.replace(' xmlns="http://xml.amadeus.com/QUERES_09_1_IA"', '')
    root = ET.fromstring(response_xml)
    rloc = GetRlocInQueue(root)
    session = get_session(root)
    
    print('rloc = ', rloc)
    return rloc, session


def StopQueue(session):
    #Input: session
    
    #session = {'SessionId': '01RKRLSYMA', 'SeqNumber': 1, 'Token': 'BBNJ90RXU4OA2Y7AIQLHGJCDM'}
    
    print('StopQueue')
    SOAPAction = 'http://webservices.amadeus.com/QUEREQ_09_1_IA'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<QueueMode_ProcessQueue>
        <messageActionDetails>
            <messageFunctionDetails>
                <messageFunction>216</messageFunction>
            </messageFunctionDetails>
        </messageActionDetails>
        <queueInfoDetails>
            <selectionInfoDetails>
                <selectionDetails>
                    <option>QP</option>
                </selectionDetails>
            </selectionInfoDetails>
        </queueInfoDetails>
    </QueueMode_ProcessQueue>"""
    
    TransactionStatusCode = 'End'
    xmlRequest = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    print(xmlRequest)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    

def PlaceQueue(rloc, QOffice, QNum, QCategory, session):
    print('PlaceQueue')
    SOAPAction = 'http://webservices.amadeus.com/QUEREQ_09_1_IA'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<QueueMode_ProcessQueue>
        <messageActionDetails>
            <messageFunctionDetails>
                <messageFunction>214</messageFunction>
            </messageFunctionDetails>
        </messageActionDetails>
        <recordLocator>
            <reservation>
                <controlNumber>{rloc}</controlNumber>
            </reservation>
        </recordLocator>
        <queueInfoDetails>
            <selectionInfoDetails>
                <selectionDetails>
                    <option>QP</option>
                </selectionDetails>
            </selectionInfoDetails>
            <queueGroup>
                <queueInfo>
                    <queueDetails>
                        <number>{QNum}</number>
                    </queueDetails>
                </queueInfo>
                <subQueueInfo>
                    <subQueueInfoDetails>
                        <identificationType>C</identificationType>
                        <itemNumber>{QCategory}</itemNumber>
                    </subQueueInfoDetails>
                </subQueueInfo>
                <subQueueInfo>
                    <subQueueInfoDetails>
                        <identificationType>4</identificationType>
                    </subQueueInfoDetails>
                </subQueueInfo>
                <targetOffice>
                    <internalIdDetails>
                        <inhouseId>{QOffice}</inhouseId>
                    </internalIdDetails>
                </targetOffice>
            </queueGroup>
        </queueInfoDetails>
    </QueueMode_ProcessQueue>"""
    
    TransactionStatusCode = 'InSeries'
    xmlRequest = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    print(xmlRequest)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    response_xml = response_xml.replace(' xmlns="http://xml.amadeus.com/QUERES_09_1_IA"', '')
    root = ET.fromstring(response_xml)
    rloc = GetRlocInQueue(root) # this function return a new rloc
    session = get_session(root)
    
    print('rloc = ', rloc)
    return rloc, session
    

def DelayQueue(rloc, delayDate, delayTime):
    # delayDate dang 15DEC23
    # delayTime dang 1400
    
    print('DelayQueue')
    SOAPAction = 'http://webservices.amadeus.com/QUEREQ_09_1_IA'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<QueueMode_ProcessQueue>
        <messageActionDetails>
            <messageFunctionDetails>
                <messageFunction>215</messageFunction>
            </messageFunctionDetails>
        </messageActionDetails>
        <recordLocator>
            <reservation>
                <controlNumber>{rloc}</controlNumber>
            </reservation>
        </recordLocator>
        <queueInfoDetails>
            <selectionInfoDetails>
                <selectionDetails>
                    <option>QP</option>
                </selectionDetails>
            </selectionInfoDetails>
            <dateTimeInfo>
                <dateAndTimeDetails>
                    <date>{delayDate}</date>
                    <time>{delayTime}</time>
                </dateAndTimeDetails>
            </dateTimeInfo>
        </queueInfoDetails>
    </QueueMode_ProcessQueue>"""
    
    xmlRequest = getRequest(SOAPAction, body)
    print(xmlRequest)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    response_xml = response_xml.replace(' xmlns="http://xml.amadeus.com/QUERES_09_1_IA"', '')
    root = ET.fromstring(response_xml)
    rloc = GetRlocInQueue(root) # this function return a new rloc
    session = get_session(root)
    
    print('rloc = ', rloc)
    return rloc, session


def QueueList(QOffice, QNum, QCategory, GdsPos, OfficePos):
    #Input: QOffice, QNum, QCategory, 
           #GdsPos dang 1A, 
           #OfficePos dang HANQH0***
    #Output: rlocs in queue, filtered by GdsPos, OfficePos
    
    print('QueueList')
    SOAPAction = 'http://webservices.amadeus.com/QDQLRQ_11_1_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<Queue_List xmlns="http://xml.amadeus.com/QDQLRQ_11_1_1A">
            <targetOffice>
                <sourceType>
                    <sourceQualifier1>4</sourceQualifier1>
                </sourceType>
                <originatorDetails>
                    <inHouseIdentification1>{QOffice}</inHouseIdentification1>
                </originatorDetails>
            </targetOffice>
            <queueNumber>
                <queueDetails>
                    <number>{QNum}</number>
                </queueDetails>
            </queueNumber>
            <categoryDetails>
                <subQueueInfoDetails>
                    <identificationType>C</identificationType>
                    <itemNumber>{QCategory}</itemNumber>
                </subQueueInfoDetails>
            </categoryDetails>
            <pos>
                <pointOfSale>
                    <partyIdentifier>{GdsPos}</partyIdentifier>
                </pointOfSale>
            </pos>
            <pos>
                <locationDetails>
                    <name>{OfficePos}</name>
                </locationDetails>
            </pos>
        </Queue_List>"""
    
    xmlRequest = getRequest(SOAPAction, body)
    print(xmlRequest)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    rlocs = []
    msg = ''
    if '<soap:Fault>' in response_xml:
        msg = getError(response_xml)
    else:
        #Loai bo namespace cho don gian:
        namespace = 'xmlns="http://xml.amadeus.com/QDQLRR_11_1_1A"'
        response_xml = response_xml.replace(namespace, '') 
        
        root = ET.fromstring(response_xml)
        Rlocs = root.findall(".//item/recLoc/reservation/controlNumber")
        
        
        for Rloc in Rlocs:
            rlocs.append(Rloc.text)

    return rlocs, msg


def QueueMoveItem(fromQOffice, fromQNum, fromQCategory, toQOffice, toQNum, toQCategory, rloc):
    #Input: fromQOffice, fromQNum, fromQCategory, toQOffice, toQNum, toQCategory, rloc
    #Output: move a PNR from one queue and category (specified under the first targetDetails) to another queue and category
    
    print('QueueMoveItem')
    SOAPAction = 'http://webservices.amadeus.com/QUQMUQ_03_1_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<Queue_MoveItem>
            <placementOption>
                <selectionDetails>
                    <option>QBB</option>
                </selectionDetails>
            </placementOption>
            <targetDetails>
                <targetOffice>
                    <sourceType>
                        <sourceQualifier1>4</sourceQualifier1>
                    </sourceType>
                    <originatorDetails>
                        <inHouseIdentification1>{fromQOffice}</inHouseIdentification1>
                    </originatorDetails>
                </targetOffice>
                <queueNumber>
                    <queueDetails>
                        <number>{fromQNum}</number>
                    </queueDetails>
                </queueNumber>
                <categoryDetails>
                    <subQueueInfoDetails>
                        <identificationType>C</identificationType>
                        <itemNumber>{fromQCategory}</itemNumber>
                    </subQueueInfoDetails>
                </categoryDetails>
            </targetDetails>
            <targetDetails>
                <targetOffice>
                    <sourceType>
                        <sourceQualifier1>4</sourceQualifier1>
                    </sourceType>
                    <originatorDetails>
                        <inHouseIdentification1>{toQOffice}</inHouseIdentification1>
                    </originatorDetails>
                </targetOffice>
                <queueNumber>
                    <queueDetails>
                        <number>{toQNum}</number>
                    </queueDetails>
                </queueNumber>
                <categoryDetails>
                    <subQueueInfoDetails>
                        <identificationType>C</identificationType>
                        <itemNumber>{toQCategory}</itemNumber>
                    </subQueueInfoDetails>
                </categoryDetails>
            </targetDetails>
            <recordLocator>
                <reservation>
                    <controlNumber>{rloc}</controlNumber>
                </reservation>
            </recordLocator>
        </Queue_MoveItem>"""

    xmlRequest = getRequest(SOAPAction, body)
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    #print(response_xml)
    
    msg = ''
    if '<soap:Fault>' in response_xml:
        msg = getError(response_xml)
        bOk = False
    else:
        #Loai bo namespace cho don gian:
        namespace = 'xmlns="http://xml.amadeus.com/QUQMUQ_03_1_1A"'
        response_xml = response_xml.replace(namespace, '') 
        
        root = ET.fromstring(response_xml)
        session = get_session(root)
        GoodRes = root.findall(".//goodResponse")
        
        bOk = GoodRes is not None
        
    return bOk, msg


def GetAvail(DepDate, FromCity, ToCity):
    #Input: DepDate, FromCity, ToCity
        # DepDate dang 310723 ddmmyy
    #Output:
    
    print('GetAvail')
    SOAPAction = 'http://webservices.amadeus.com/SATRQT_19_1_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<Air_MultiAvailability>
	<messageActionDetails>
		<functionDetails>
			<businessFunction>1</businessFunction>
			<actionCode>44</actionCode>
		</functionDetails>
	</messageActionDetails>
	<requestSection>
		<availabilityProductInfo>
			<availabilityDetails>
				<departureDate>{DepDate}</departureDate>
			</availabilityDetails>
			<departureLocationInfo>
				<cityAirport>{FromCity}</cityAirport>
			</departureLocationInfo>
			<arrivalLocationInfo>
				<cityAirport>{ToCity}</cityAirport>
			</arrivalLocationInfo>
		</availabilityProductInfo>
		<availabilityOptions>
			<typeOfRequest>TN</typeOfRequest>
		</availabilityOptions>
	</requestSection>
</Air_MultiAvailability>"""

    xmlRequest = getRequest(SOAPAction, body)
    response = requests.post(url, data=xmlRequest, headers=headers)
    
    response_xml = response.content.decode("utf-8")
    #print(response_xml)

    lines = []
    msg = ''
    session = None
    
    if '<soap:Fault>' in response_xml:
        msg = getError(response_xml)
    else:
        #Loai bo namespace cho don gian:
        namespace = 'xmlns="http://xml.amadeus.com/SATRSP_19_1_1A"'
        response_xml = response_xml.replace(namespace, '') 
        
        #tree = ET.parse('avail_response.xml')
        #root = tree.getroot()
        #Neu co namespace: https://docs.python.org/3/library/xml.etree.elementtree.html
        #Flts = root.findall(".//{http://xml.amadeus.com/SATRSP_19_1_1A}flightInfo")
        
        root = ET.fromstring(response_xml)
        #info = root[1][0][1] # root[1] la Body, --> singleCityPairInfo
        Flts = root.findall(".//flightInfo")
        
        #departureDate = Flts[0][0][0][0].text # 250723
        for flt in Flts:
            DepDateStr = flt.find(".//departureDate").text
            DepDate = datetime.datetime.strptime(DepDateStr, '%d%m%y')
            DepTime = flt.find(".//departureTime").text
            ArrDateStr = flt.find(".//arrivalDate").text
            ArrDate = datetime.datetime.strptime(ArrDateStr, '%d%m%y')
            ArrTime = flt.find(".//arrivalTime").text
            FltNum = flt.find('.//flightIdentification/number').text
            Classes = flt.findall('.//infoOnClasses')
            
            line = f'{DepDate.strftime("%d-%b-%Y")}/{DepTime}/{ArrDate.strftime("%d-%b-%Y")}/{ArrTime}/QH{FltNum}'
            lines.append(line)
            line = ''
            for cls in Classes:
                RBD = cls.find('.//serviceClass').text
                AvailStr = cls.find('.//availabilityStatus').text
                Avail = 0 if AvailStr.strip() == '' else int(AvailStr)
                line += f'{RBD}{Avail} '
                
            lines.append(line)
            
        session = get_session(root)
        
    return lines, msg, session


def get_paxname(root):
    #Input: root
    #Output: list of pax names or group name
    
    print('get_paxname')
    names = []
    
    Names = root.findall(".//travellerInfo/passengerData/travellerInformation")
    PnrType = root.find(".//travellerInfo/elementManagementPassenger/segmentName").text
    if PnrType == 'NM': # Non Group PNR
        for Name in Names:
            surname = Name.find('traveller/surname').text
            firstName = Name.find('passenger/firstName').text
            paxType = Name.find('passenger/type')
            paxType = '' if paxType is None else paxType.text
            quantity = int(Name.find('traveller/quantity').text)
            #names.append({'surname': surname, 'firstName': firstName, 'paxType': paxType, 'quantity': quantity})
            name = pnr_class.pax_name(surname, firstName, paxType, quantity)
            names.append(name)
    else: # Group PNR
        Name = Names[0] # lay Group name:
        surname = Name.find('traveller/surname').text
        firstName = ''
        paxType = Name.find('traveller/qualifier')
        paxType = '' if paxType is None else paxType.text
        quantity = int(Name.find('traveller/quantity').text)
        
        #names.append({'surname': surname, 'firstName': firstName, 'paxType': paxType, 'quantity': quantity})
        name = pnr_class.pax_name(surname, firstName, paxType, quantity)
        names.append(name)
        
    return names


def get_contact(root):
    #Input: root
    #Output: list of pax tel and email
    
    print('get_contact')
    contacts = []
    '''
    /dataElementsMaster/dataElementsIndiv[1]/otherDataFreetext/longFreetext
    <dataElementsMaster>
        <marker2></marker2>
        <dataElementsIndiv>
            <elementManagementData>
                <reference>
                    <qualifier>OT</qualifier>
                    <number>13</number>
                </reference>
                <segmentName>AP</segmentName>  --> Contact element
                <lineNumber>2</lineNumber>
            </elementManagementData>
            <otherDataFreetext>
                <freetextDetail>
                    <subjectQualifier>3</subjectQualifier>
                    <type>5</type>
                </freetextDetail>
                <longFreetext>D@GMAIL.COM</longFreetext>
            </otherDataFreetext>
        </dataElementsIndiv>
        
                <longFreetext>84800008509-H</longFreetext> --> phone
                <longFreetext>+84 905581268</longFreetext>
                <longFreetext>HAN 90413338 - BAMBOO AIRWAYS ALTEA PLAN OFC AT HQ HAN - A</longFreetext>
                <longFreetext>M +84905581268</longFreetext> --> mobi phone
                <longFreetext>H +84397097915</longFreetext> --> home --> not take
                <longFreetext>E HDQSCQH@BAMBOOAIRWAYS.COM</longFreetext> --> email
    '''
    
    Contacts = root.findall('.//dataElementsMaster/dataElementsIndiv')
    for ele in Contacts:
        segmentName = ele.find('elementManagementData/segmentName').text
        if segmentName == 'AP': # Contact element
            data = ele.find('otherDataFreetext/longFreetext').text
            t = 'email' if '@' in data else 'phone'
            if t == 'phone': # phone_number = '+55(11)8715-9877'
                if data[0] in ['M', '+'] or data[0].isdigit(): # mobi phone
                    #Chi lay cac ky tu so:
                    data = ''.join([n for n in data if n.isdigit()])
                    
                    # txt = "h3110 23 cat 444.4 rabbit 11 2 dog"
                    #[int(s) for s in txt.split() if s.isdigit()] --> extract only positive integers
                    #data = re.sub(r"\D", "", data)
                else:
                    data = '' # not get home phone
            else: # email
                if data[0] == 'E': data = data[1:].strip()

            if data != '':
                contact = pnr_class.pax_contact(t, data) 
                #contact = {'type': t, 'data': data}
                if contact not in contacts: # not duplicated
                    contacts.append(contact)
            
        elif segmentName == 'SSR': # SSR element
            #ssr_ele = ele.find('serviceRequest/ssr/type[.="CTCM"]/..')
            #or ssr_ele = tree.find('.//serviceRequest/ssr/type[.="CTCM"]...')
            # tree.findall('.//child[@id="123"]...') # @: attribute
            # node.tag, node.attrib, node.text
            
            # contact mobi phone: lay ssr ele co child type.text = "CTCM"
            #data = ssr_ele.find('freeText').text
            
            ssr_ele = ele.find('serviceRequest/ssr')
            if ssr_ele is not None:
                type_text = ssr_ele.find('type').text
                
                if type_text == 'CTCE':
                    t = 'email'
                elif type_text == 'CTCM': 
                    t = 'phone'
                else:
                    t = ''
                    
                if t != '':
                    data = ssr_ele.find('freeText').text
                    print('data = ', data)
                    #<freeText>HDQSCQH//BAMBOOAIRWAYS.COM</freeText>
                    if t == 'email' :
                        data = data.replace(r'//', '@')
                    else:
                        data = ''.join([n for n in data if n.isdigit()])

                    if data != '':
                        contact = pnr_class.pax_contact(t, data)
                        if contact not in contacts:
                            contacts.append(contact)

    return contacts


def PNR_Retrieve_Active(session):
    #Input: session
    #Output: Retrieve active pnr, so no need rloc
    #        msg
    
    print('PNR_Retrieve_Active')
    if session == None:
        raise Exception('You have to provide session to do this function!')
    
    SOAPAction = 'http://webservices.amadeus.com/PNRRET_21_1_1A' # get this from tag wsa:Action
    
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<PNR_Retrieve>
    <retrievalFacts>
        <retrieve>
            <type>1</type>
        </retrieve>
    </retrievalFacts>
</PNR_Retrieve>"""
        
    TransactionStatusCode = "InSeries"
    request_xml = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    print('Request = ')
    print(request_xml)
    
    response = requests.post(url, data=request_xml, headers=headers)
    response_xml = response.content.decode("utf-8")
    
    print('Response = ')
    print(response_xml)

    pnr = None
    msg = ''

    if '<soap:Fault' in response_xml:
        msg = getError(response_xml)
    else:
        #tree = ET.parse('C:/Temp/API_RT_PNR_Response.txt')
        #root = tree.getroot()
        
        #with open("C:/Temp/API_RT_PNR_Response.txt", "r") as f:
        #    response_xml = f.read()
            
        namespace = ' xmlns="http://xml.amadeus.com/PNRACC_21_1_1A"'
        response_xml = response_xml.replace(namespace, '') 

        root = ET.fromstring(response_xml)

        names = get_paxname(root)
        
        contacts = get_contact(root)
        
        segments = get_segments(root)
    
        #pnr = {'rloc': rloc, 'names': names, 'segments': segments, 'contacts': contacts}
        pnr = pnr_class.pnr_class(rloc, names, segments, contacts)
        
    return pnr, msg


def PNR_Retrieve(rloc, session=None):
    #Input: rloc, session
    #Output: pnr, session, msg
    
    print('PNR_Retrieve')
    print(f'rloc = {rloc}')
    
    SOAPAction = 'http://webservices.amadeus.com/PNRRET_21_1_1A' # get this from tag wsa:Action
    
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<PNR_Retrieve>
	      <retrievalFacts>
	        <retrieve>
	          <type>2</type>
	        </retrieve>
	        <reservationOrProfileIdentifier>
	          <reservation>
	            <controlNumber>{rloc}</controlNumber>
	          </reservation>
	        </reservationOrProfileIdentifier>
	      </retrievalFacts>
	    </PNR_Retrieve>"""
        
    if session == None:
        request_xml = getRequest(SOAPAction, body)
    else:
        TransactionStatusCode = "InSeries"
        request_xml = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    print('Request = ')
    print(request_xml)
    
    response = requests.post(url, data=request_xml, headers=headers)
    response_xml = response.content.decode("utf-8")
    
    print('Response = ')
    print(response_xml)

    '''
    <travellerInfo>
        <elementManagementPassenger>
            <segmentName>NG</segmentName>  #NG --> Group PNR
            <lineNumber>0</lineNumber>
        </elementManagementPassenger>
        <passengerData>
            <travellerInformation>
                <traveller>
                    <surname>ABC</surname>
                    <qualifier>G</qualifier>
                    <quantity>11</quantity>
                </traveller>
            </travellerInformation>
            
        </passengerData>
    </travellerInfo>
    
    <travellerInfo>
        <elementManagementPassenger>
            <reference>
                <qualifier>PT</qualifier>
                <number>1</number>
            </reference>
            <segmentName>NM</segmentName> #NM --> Non Group PNR
            <lineNumber>1</lineNumber>
        </elementManagementPassenger>
    </travellerInfo>
    '''
    
    pnr = None
    msg = ''

    if '<soap:Fault' in response_xml:
        msg = getError(response_xml)
    else:
        #tree = ET.parse('C:/Temp/API_RT_PNR_Response.txt')
        #root = tree.getroot()
        
        #with open("C:/Temp/API_RT_PNR_Response.txt", "r") as f:
        #    response_xml = f.read()
            
        namespace = ' xmlns="http://xml.amadeus.com/PNRACC_21_1_1A"'
        response_xml = response_xml.replace(namespace, '') 

        root = ET.fromstring(response_xml)

        names = get_paxname(root)
        
        contacts = get_contact(root)
        
        segments = get_segments(root)
    
        #pnr = {'rloc': rloc, 'names': names, 'segments': segments, 'contacts': contacts}
        pnr = pnr_class.pnr_class(rloc, names, segments, contacts)
        
        if session == None:
            session = get_session(root)

    return pnr, session, msg


def get_session(root):
    #Input: root
    #Output: session info
    
    print('get_session')

    namespaces = {'awsse': 'http://xml.amadeus.com/2010/06/Session_v3'} # add more as needed
    Sess = root.find('.//awsse:Session', namespaces)
    #print('Sess = ', Sess) # <Element '{http://xml.amadeus.com/2010/06/Session_v3}Session' at 0x0000017A07700E50>
    
    SessionId = Sess.find('awsse:SessionId', namespaces).text
    SeqNumber = int(Sess.find('awsse:SequenceNumber', namespaces).text)
    Token = Sess.find('awsse:SecurityToken', namespaces).text
    session = {'SessionId': SessionId, 'SeqNumber': SeqNumber, 'Token': Token}
    print('session = ', session)
    return session


def Cryptic_Sess(cmd, session, TransactionStatusCode):
    #Input: cmd, session, TransactionStatusCode
    #Output:
    print('Cryptic_Sess')
    SOAPAction = 'http://webservices.amadeus.com/HSFREQ_07_3_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    # TransactionStatusCode="InSeries" # End
    
    body = f"""<Command_Cryptic>
         <messageAction>
            <messageFunctionDetails>
               <messageFunction>M</messageFunction>
            </messageFunctionDetails>
         </messageAction>
         <longTextString>
            <textStringDetails>{cmd}</textStringDetails>
         </longTextString>
      </Command_Cryptic>"""

    xmlRequest = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    print('\nxmlRequest = \n', xmlRequest)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print('\nResponse:\n')
    print(response_xml)
    
    text = ''
    msg = ''
    if '<soap:Fault>' in response_xml:
        msg = getError(response_xml)
    else:
        namespace = 'xmlns="http://xml.amadeus.com/HSFRES_07_3_1A"'
        response_xml = response_xml.replace(namespace, '') 
        
        root = ET.fromstring(response_xml)
        text_ele = root.find(".//longTextString/textStringDetails")
        if text_ele is not None:
            text = text_ele.text[2:] if text_ele.text[:2] == '/$' else text_ele.text # bo '/$' o dau
            text = text.strip()
    #print('text = ', text)

    return text, msg


def Cryptic(cmd):
    #Input: cmd
    #Output:
    print('Cryptic')
    SOAPAction = 'http://webservices.amadeus.com/HSFREQ_07_3_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<Command_Cryptic>
         <messageAction>
            <messageFunctionDetails>
               <messageFunction>M</messageFunction>
            </messageFunctionDetails>
         </messageAction>
         <longTextString>
            <textStringDetails>{cmd}</textStringDetails>
         </longTextString>
      </Command_Cryptic>"""

    xmlRequest = getRequest(SOAPAction, body)
    print('xmlRequest = ', xmlRequest)
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    text = ''
    msg = ''
    if '<soap:Fault>' in response_xml:
        msg = getError(response_xml)
    else:
        namespace = 'xmlns="http://xml.amadeus.com/HSFRES_07_3_1A"'
        response_xml = response_xml.replace(namespace, '') 
        
        root = ET.fromstring(response_xml)
        text = root.find(".//longTextString/textStringDetails").text
    print('text = ', text)
        
    return text, msg


def ListPax(flt, year, month, day, boardPoint, offPoint):
    #Input: flt, year, month, day, boardPoint, offPoint
    #Output: rlocs, err_msg, session
    
    print('ListPax')
    SOAPAction = 'http://webservices.amadeus.com/PALPRQ_14_1_1A' # UAT
    #SOAPAction = 'http://webservices.amadeus.com/PALPRQ_13_1_1A' # Production
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<PNR_ListPassengersByFlight xmlns="http://xml.amadeus.com/PALPRQ_14_1_1A">
            <flightDateQuery>
                <flightIdentification>
                    <carrierDetails>
                        <marketingCarrier>QH</marketingCarrier>
                    </carrierDetails>
                    <flightDetails>
                        <flightNumber>{flt}</flightNumber>
                    </flightDetails>
                    <boardPoint>{boardPoint}</boardPoint>
                    <offPoint>{offPoint}</offPoint>
                </flightIdentification>
                <dateIdentification>
                    <businessSemantic>FDD</businessSemantic>
                    <dateTime>
                        <year>{year}</year>
                        <month>{month}</month>
                        <day>{day}</day>
                    </dateTime>
                </dateIdentification>
                <outputSelectionOption>
                    <outputType>
                        <selectionDetails>
                            <option>IMG</option>
                        </selectionDetails>
                    </outputType>
                     <elementType>
                        <segmentName>HDR</segmentName>
                    </elementType>
                </outputSelectionOption>
            </flightDateQuery>
        </PNR_ListPassengersByFlight>"""

    xmlRequest = getRequest(SOAPAction, body)
    print(xmlRequest)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    rlocs = []
    err_msg = ''
    session = None
    
    if '<soap:Fault>' in response_xml:
        err_msg = getError(response_xml)
    else:
        namespace = 'xmlns="http://xml.amadeus.com/PALPRR_14_1_1A"'
        response_xml = response_xml.replace(namespace, '') 
        
        root = ET.fromstring(response_xml)
        Rlocs = root.findall(".//pnrView/amadeusId/reservation/controlNumber")
        
        for Rloc in Rlocs:
            rloc = Rloc.text
            rlocs.append(rloc)
            
        session = get_session(root)

    return rlocs, err_msg, session
    
    
def GetFlightInven(flt, depDate):
    #Input: 
    #Output:
    print('GetFlightInven')
    SOAPAction = 'http://webservices.amadeus.com/IFLIRQ_15_2_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<Inv_AdvancedGetFlightData>
            <flightDate>
                <airlineInformation>
                    <airlineCode>QH</airlineCode>
                </airlineInformation>
                <flightReference>
                    <flightNumber>{flt}</flightNumber>
                </flightReference>
                <departureDate>{depDate}</departureDate>
            </flightDate>
            <grabLock>
                <statusInformation>
                    <statusIndicator>GBL</statusIndicator>
                    <actionRequest>2</actionRequest>
                </statusInformation>
            </grabLock>
        </Inv_AdvancedGetFlightData>"""
    
    xmlRequest = getRequest(SOAPAction, body)
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    legs = []
    msg = ''
    if '<soap:Fault>' in response_xml:
        msg = getError(response_xml)
    else:
        namespace = 'xmlns="http://xml.amadeus.com/IFLIRR_15_2_1A"'
        response_xml = response_xml.replace(namespace, '') 
        
        root = ET.fromstring(response_xml)
        Legs = root.findall(".//legs")
        #print('len(Legs) = ', len(Legs))
        
        for Leg in Legs:
            Cities = Leg.findall('leg/legDetails/locations')
            depCity = Cities[0].text
            arrCity = Cities[1].text
            
            Cabins = Leg.findall("legCabins")
            cabins = []
            for Cabin in Cabins:
                Config = Cabin.find('legCabin/fittedConfiguration') # first fittedConfiguration element
                cabinCode = Config.find('cabinCode').text
                cap = int(Config.find('cabinCapacity').text)
                qualifier = Config.find('qualifier').text
                
                Avail = Cabin.find('cabinAvailabilities')
                bkg = int(Avail.find('bookingsCounter').text)
                netAvail = int(Avail.find('netAvailability').text)
                grossAvail = int(Avail.find('grossAvailability').text)
                
                cabin = {'cabinCode': cabinCode, 'cap': cap, 'qualifier': qualifier,
                         'bkg': bkg, 'netAvail': netAvail, 'grossAvail': grossAvail}
                cabins.append(cabin)
                
            leg = {'depCity': depCity, 'arrCity': arrCity, 'cabins': cabins}
            legs.append(leg)
            
    return legs, msg


def PNR_AddMultiElements_TST_Display(rloc):
    #Input: session, TransactionStatusCode
    #Output:
    
    print('PNR_AddMultiElements_TST_Display')
    SOAPAction = 'http://webservices.amadeus.com/PNRADD_21_1_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<PNR_AddMultiElements>
    <reservationInfo>
        <reservation>
            <controlNumber>{rloc}</controlNumber>
        </reservation>
    </reservationInfo>
    <pnrActions>
        <optionCode>0</optionCode>
    </pnrActions>
</PNR_AddMultiElements>"""
    
    xmlRequest = getRequest(SOAPAction, body)
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    #print(response_xml)
    
    msg = ''
    paxs = []
    if '<soap:Fault>' in response_xml:
        msg = getError(response_xml)
        print(msg)
    else:
        namespace = 'xmlns="http://xml.amadeus.com/PNRACC_21_1_1A"'
        response_xml = response_xml.replace(namespace, '') 
        
        root = ET.fromstring(response_xml)
        Paxs = root.findall(".//travellerInfo/passengerData/travellerInformation")
        for Pax in Paxs:
            surname = Pax.find('traveller/surname').text
            firstName = Pax.find('passenger/firstName').text
            TypePax = Pax.find('passenger/type')
            typePax = '' if TypePax is None else TypePax.text
            
            paxs.append({'surname': surname, 'firstName': firstName, 'type': typePax})
    return paxs, msg

'''
Option Code Description
10: End transact (ET)

11: End transact with retrieve (ER)

12: End transact and change advice codes (ETK)

13: End transact with retrieve and change advice codes (ERK)

14: End transact split PNR (EF)

20: Ignore (IG)

21: Ignore with retrieve (IR)
'''

def PNR_AddRMK(rloc, rmk, session):
    #Input: rloc, rmk, session
    #Output: add RMKs to PNR
    
    print('PNR_AddRMK')
    SOAPAction = 'http://webservices.amadeus.com/PNRADD_21_1_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<PNR_AddMultiElements>
  <reservationInfo>
    <reservation>
      <controlNumber>{rloc}</controlNumber>
    </reservation>
  </reservationInfo>
  <pnrActions>
    <optionCode>11</optionCode>
  </pnrActions>
  <dataElementsMaster>
    <marker1/>
    <dataElementsIndiv>
      <elementManagementData>
        <reference>
          <qualifier>OT</qualifier>
          <number>1</number>
        </reference>
        <segmentName>RM</segmentName>
      </elementManagementData>
      <miscellaneousRemark>
        <remarks>
          <type>RM</type>
          <freetext>GENERAL REMARK {rmk}</freetext>
        </remarks>
      </miscellaneousRemark>
    </dataElementsIndiv>
    <dataElementsIndiv>
      <elementManagementData>
        <reference>
          <qualifier>OT</qualifier>
          <number>2</number>
        </reference>
        <segmentName>RM</segmentName>
      </elementManagementData>
      <miscellaneousRemark>
        <remarks>
          <type>RM</type>
          <category>M</category>
          <freetext>CATEGORY M {rmk}</freetext>
        </remarks>
      </miscellaneousRemark>
    </dataElementsIndiv>
    <dataElementsIndiv>
      <elementManagementData>
        <reference>
          <qualifier>OT</qualifier>
          <number>3</number>
        </reference>
        <segmentName>RC</segmentName>
      </elementManagementData>
      <miscellaneousRemark>
        <remarks>
          <type>RC</type>
          <freetext>CONFIDENTIAL REMARK THAT ONLY AGENCY CAN SEE {rmk}</freetext>
        </remarks>
      </miscellaneousRemark>
    </dataElementsIndiv>
    <dataElementsIndiv>
        <elementManagementData>
            <segmentName>RF</segmentName>
        </elementManagementData>
        <freetextData>
            <freetextDetail>
                <subjectQualifier>3</subjectQualifier>
                <type>P22</type>
            </freetextDetail>
            <longFreetext>RF ROBOT</longFreetext>
        </freetextData>
    </dataElementsIndiv>
  </dataElementsMaster>
</PNR_AddMultiElements>"""

    #xmlRequest = getRequest(SOAPAction, body)
    TransactionStatusCode = 'InSeries'
    xmlRequest = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    msg = ''
    paxs = []
    '''
    if '<soap:Fault>' in response_xml:
        msg = getError(response_xml)
        print(msg)
    else:
        namespace = 'xmlns="http://xml.amadeus.com/PNRACC_21_1_1A"'
        response_xml = response_xml.replace(namespace, '') 
        
        root = ET.fromstring(response_xml)
        Paxs = root.findall(".//travellerInfo/passengerData/travellerInformation")
        for Pax in Paxs:
            surname = Pax.find('traveller/surname').text
            firstName = Pax.find('passenger/firstName').text
            TypePax = Pax.find('passenger/type')
            typePax = '' if TypePax is None else TypePax.text
            
            paxs.append({'surname': surname, 'firstName': firstName, 'type': typePax})
    '''
    return paxs, msg


def PNR_Add_ReceivedFrom(session):
    #Input: session
    #Output: add ReceivedFrom element to PNR to end transaction
    
    print('PNR_Add_ReceivedFrom')
    SOAPAction = 'http://webservices.amadeus.com/PNRADD_21_1_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<PNR_AddMultiElements>
  <pnrActions>
    <optionCode>10</optionCode>
  </pnrActions>
  <dataElementsMaster>
    <marker1 />
    <dataElementsIndiv>
        <elementManagementData>
            <segmentName>RF</segmentName>
        </elementManagementData>
        <freetextData>
            <freetextDetail>
                <subjectQualifier>3</subjectQualifier>
                <type>P22</type>
            </freetextDetail>
            <longFreetext>RF ROBOT</longFreetext>
        </freetextData>
    </dataElementsIndiv>
  </dataElementsMaster>
</PNR_AddMultiElements>"""
    
    TransactionStatusCode = 'InSeries'
    xmlRequest = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    #xmlRequest = getRequest(SOAPAction, body)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)


def PNR_AddSegment(segment, session):
    #Input: segment, session
    #Output: add segment and ReceivedFrom element to PNR to end transaction
    
    print('PNR_AddSegment')
    SOAPAction = 'http://webservices.amadeus.com/PNRADD_21_1_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    #segment = {'FromCity': 'SGN', 'ToCity': 'HAN', 'DepDate': '020923', 'RBD': 'Q', 'Flt':'202', 'NumPax': 1, 'Status': 'SG'}
    #Status = SG / PG for group pnr; NN for non group
    
    body = f"""<PNR_AddMultiElements>
  <pnrActions>
    <optionCode>10</optionCode>
  </pnrActions>
  <originDestinationDetails>
    <originDestination>
        <origin>{segment['FromCity']}</origin>
        <destination>{segment['ToCity']}</destination>
    </originDestination>
    <itineraryInfo>
        <elementManagementItinerary>
            <segmentName>AIR</segmentName>
        </elementManagementItinerary>
        <airAuxItinerary>
            <travelProduct>
                <product>
                    <depDate>{segment['DepDate']}</depDate>
                </product>
                <boardpointDetail>
                    <cityCode>{segment['FromCity']}</cityCode>
                </boardpointDetail>
                <offpointDetail>
                    <cityCode>{segment['ToCity']}</cityCode>
                </offpointDetail>
                <company>
                    <identification>QH</identification>
                </company>
                <productDetails>
                    <identification>{segment['Flt']}</identification>
                    <classOfService>{segment['RBD']}</classOfService>
                </productDetails>
            </travelProduct>
            <messageAction>
                <business>
                    <function>1</function>
                </business>
            </messageAction>
            <relatedProduct>
                <quantity>{segment['NumPax']}</quantity>
                <status>{segment['Status']}</status>
            </relatedProduct>
        </airAuxItinerary>
    </itineraryInfo>
  </originDestinationDetails>
  <dataElementsMaster>
    <marker1 />
    <dataElementsIndiv>
        <elementManagementData>
            <segmentName>RF</segmentName>
        </elementManagementData>
        <freetextData>
            <freetextDetail>
                <subjectQualifier>3</subjectQualifier>
                <type>P22</type>
            </freetextDetail>
            <longFreetext>RF ROBOT</longFreetext>
        </freetextData>
    </dataElementsIndiv>
  </dataElementsMaster>
</PNR_AddMultiElements>"""
    
    '''
    <dataElementsIndiv>
        <elementManagementData>
            <segmentName>TK</segmentName>
        </elementManagementData>
        <ticketElement>
            <passengerType>PAX</passengerType>
            <ticket>
                <indicator>OK</indicator>
            </ticket>
        </ticketElement>
    </dataElementsIndiv>
    '''
    
    TransactionStatusCode = 'InSeries'
    xmlRequest = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    #xmlRequest = getRequest(SOAPAction, body)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)


'''
The cancelElements/entry type below are used to cancel elements. Only one type can be entered in a single Cancel request. For multiple cancel type, several calls must be done:

D: Cancel Duplicate segments (TTY message not sent to the airline)

E: Cancel element type

G: G Name integration

I: Cancel itinerary type

P: Priority line type

S: Cancel ES element

=========
PNR Qualifier or element -> identifier
    1. PT (Passenger Tattoo): Name element, Group element
    2. ST (Segment Tattoo): Air Segment, Hotel element, Car element, Miscellaneous element
    3. OT (Other element Tattoo): (non name, non segment): Remark, Contact, SSR, OSI, ...
    4. OOT: An offer is an item proposition, in other words, a set availability and quotation, made to the customer before booking, with no guarantee of price and availability.
    
=========
cancelElements -> entryType:
    D: D type, Cancel Duplicate segments (TTY message not sent to the airline)

    E: XE: Cancel element type

    G: G Name integration

    I: XI: Cancel itinerary type

    P: Priority line type

    S: ESX: Cancel ES element (Extended Contents)
=========
pnrActions -> optionCode = 10: EOT
                         = 11: EOT and Redisplay PNR
'''

def PNR_Cancel(rloc, element, session):
    #Input: rloc, element, session
    #Output: Cancel element (Segment, RMKs) of PNR
    
    #element = {'identifier': 'OT', 'number': 130} # RMK
    #element = {'identifier': 'ST', 'number': 7} # Segment
    
    print('PNR_Cancel')
    SOAPAction = 'http://webservices.amadeus.com/PNRXCL_21_1_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<PNR_Cancel>
    <reservationInfo>
        <reservation>
          <controlNumber>{rloc}</controlNumber>
        </reservation>
    </reservationInfo>
    <pnrActions>
        <optionCode>10</optionCode>
    </pnrActions>
    <cancelElements>
        <entryType>E</entryType>
        <element>
          <identifier>{element['identifier']}</identifier>
          <number>{element['number']}</number>
        </element>
    </cancelElements>
</PNR_Cancel>"""

    #xmlRequest = getRequest(SOAPAction, body)
    TransactionStatusCode = 'InSeries'
    xmlRequest = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    
    response = requests.post(url, data=xmlRequest, headers=headers)
    response_xml = response.content.decode("utf-8")
    print(response_xml)
    
    msg = ''
    paxs = []
    if '<soap:Fault>' in response_xml:
        msg = getError(response_xml)
        print(msg)
    else:
        namespace = 'xmlns="http://xml.amadeus.com/PNRACC_21_1_1A"'
        response_xml = response_xml.replace(namespace, '') 
        
        root = ET.fromstring(response_xml)
        Paxs = root.findall(".//travellerInfo/passengerData/travellerInformation")
        for Pax in Paxs:
            surname = Pax.find('traveller/surname').text
            firstName = Pax.find('passenger/firstName').text
            TypePax = Pax.find('passenger/type')
            typePax = '' if TypePax is None else TypePax.text
            
            p_name = pnr_class.pax_name(surname, firstName, typePax)
            paxs.append(p_name)
            #paxs.append({'surname': surname, 'firstName': firstName, 'type': typePax})
    return paxs, msg


def get_seg_qualifier(segments, segment):
    #Input: segments, segment
    #Output: qualifier cua segment trong segments, de huy segment
    #QH 201 K 01SEP 5 HANSGN HN11
    
    print('get_seg_qualifier')
    qualifier = 0
    for seg in segments:
        if seg['DepDate'] == segment['DepDate'] and seg['FromCity']+seg['ToCity'] == segment['FromCity']+segment['ToCity'] and \
           seg['Carrier'] + seg['Flt'] == segment['Carrier'] + segment['Flt'] and seg['RBD'] == segment['RBD'] and \
           seg['NumPax'] == segment['NumPax'] and seg['Status'] == segment['Status']:
            qualifier = seg['Qualifier']
            break

    return qualifier


def get_segments(root):
    #Input: root la 1 xml element
    #Output: cac segments
    
    segments = []
    print('get_segments')
    
    itins = root.findall('.//originDestinationDetails/itineraryInfo')
    for itin in itins:
        qualifier = itin.find('elementManagementItinerary/reference/qualifier').text
        segmentName = itin.find('elementManagementItinerary/segmentName').text
        if qualifier == 'ST' and segmentName == 'AIR':
            qualifier_num = int(itin.find('elementManagementItinerary/reference/number').text)
            lineNumber = itin.find('elementManagementItinerary/lineNumber').text
            
            flt = itin.find('travelProduct')
            depDate = flt.find('product/depDate').text
            depTime = flt.find('product/depTime').text
            arrDate = flt.find('product/arrDate').text
            arrTime = flt.find('product/arrTime').text
            FromCity = flt.find('boardpointDetail/cityCode').text
            ToCity = flt.find('offpointDetail/cityCode').text
            Carrier = flt.find('companyDetail/identification').text
            fltnbr  = flt.find('productDetails/identification').text
            RBD     = flt.find('productDetails/classOfService').text
            NumPax  = int(itin.find('relatedProduct/quantity').text)
            Status  = itin.find('relatedProduct/status').text
            
            #segment = {'Qualifier': qualifier_num, 'LineNum': lineNumber, 'DepDate': depDate, 'DepTime': depTime,
            #           'ArrDate': arrDate, 'ArrTime': arrTime, 'FromCity': FromCity, 'ToCity': ToCity, 'Carrier': Carrier,
            #           'Flt': fltnbr, 'RBD': RBD, 'NumPax': NumPax, 'Status': Status}
            
            segment = pnr_segment.pnr_segment(qualifier_num, lineNumber, depDate, depTime, arrDate, arrTime, FromCity, ToCity, Carrier, fltnbr, RBD, NumPax, Status)
            
            segments.append(segment)
            
    return segments


def PNR_Rebook(session, FromSeg, ToSeg):
    #Input: session, FromSeg, ToSeg
    #Output: rebook QH201/01Sep23 from H to K class
    #segment = {'FromCity': 'SGN', 'ToCity': 'HAN', 'DepDate': '020923','DepTime':'0535','RBD': 'Q', 'Flt':'202', 'NumPax': 1}
    
    print('PNR_Rebook')
    SOAPAction = 'http://webservices.amadeus.com/ARBKUQ_20_1_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<Air_RebookAirSegment>
	<originDestinationDetails>
		<originDestination>
			<origin>{ToSeg['FromCity']}</origin>
			<destination>{ToSeg['ToCity']}</destination>
		</originDestination>
		<itineraryInfo>
			<flightDetails>
				<flightDate>
					<departureDate>{FromSeg['DepDate']}</departureDate>
					<departureTime>{FromSeg['DepTime']}</departureTime>
				</flightDate>
				<boardPointDetails>
					<trueLocationId>{FromSeg['FromCity']}</trueLocationId>
				</boardPointDetails>
				<offpointDetails>
					<trueLocationId>{FromSeg['ToCity']}</trueLocationId>
				</offpointDetails>
				<companyDetails>
					<marketingCompany>QH</marketingCompany>
				</companyDetails>
				<flightIdentification>
					<flightNumber>{FromSeg['Flt']}</flightNumber>
					<bookingClass>{FromSeg['RBD']}</bookingClass>
				</flightIdentification>
			</flightDetails>
			<relatedFlightInfo>
				<quantity>{FromSeg['NumPax']}</quantity>
				<statusCode>OX</statusCode>
			</relatedFlightInfo>
		</itineraryInfo>
		<itineraryInfo>
			<flightDetails>
				<flightDate>
					<departureDate>{ToSeg['DepDate']}</departureDate>
					<departureTime>{ToSeg['DepTime']}</departureTime>
				</flightDate>
				<boardPointDetails>
					<trueLocationId>{ToSeg['FromCity']}</trueLocationId>
				</boardPointDetails>
				<offpointDetails>
					<trueLocationId>{ToSeg['ToCity']}</trueLocationId>
				</offpointDetails>
				<companyDetails>
					<marketingCompany>QH</marketingCompany>
				</companyDetails>
				<flightIdentification>
					<flightNumber>{ToSeg['Flt']}</flightNumber>
					<bookingClass>{ToSeg['RBD']}</bookingClass>
				</flightIdentification>
			</flightDetails>
			<relatedFlightInfo>
				<quantity>{ToSeg['NumPax']}</quantity>
				<statusCode>NN</statusCode>
			</relatedFlightInfo>
		</itineraryInfo>
	</originDestinationDetails>
</Air_RebookAirSegment>"""

    TransactionStatusCode = 'InSeries'
    xmlRequest = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    response = requests.post(url, data=xmlRequest, headers=headers)
    
    response_xml = response.content.decode("utf-8")
    print(response_xml)


def getFlightInfo(session, flt, depDate):
    #Input: session, flt, depDate dang ddmmyy
    #Output: 
    
    print('getFlightInfo')
    SOAPAction = 'http://xml.amadeus.com/FLIREQ_07_1_1A'
    headers = {'content-type': 'application/xml', 'Cache-Control': 'no-cache', 'SOAPAction': SOAPAction}
    
    body = f"""<Air_FlightInfo xmlns="http://xml.amadeus.com/FLIREQ_07_1_1A">
    <generalFlightInfo>
        <flightDate>
            <departureDate>{depDate}</departureDate>
        </flightDate>
        <companyDetails>
            <marketingCompany>QH</marketingCompany>
        </companyDetails>
        <flightIdentification>
            <flightNumber>{flt}</flightNumber>
        </flightIdentification>
    </generalFlightInfo>
</Air_FlightInfo>"""
    
    TransactionStatusCode = 'InSeries'
    xmlRequest = getRequestBySession(SOAPAction, body, session, TransactionStatusCode)
    response = requests.post(url, data=xmlRequest, headers=headers)
    
    response_xml = response.content.decode("utf-8")
    print(response_xml)



nonce = generateRandomString(12)
#timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z' #"2023-06-09T02:40:21.850Z"
timestamp = datetime.datetime.utcnow().isoformat(sep='T', timespec='milliseconds') + 'Z'

saltedLSSPass = saltPassword(nonce, timestamp, password) #YwcJYkHJvUkMRaMT0vnZd0eovmg=

nonceBase64 = toBase64(toBytes(nonce))
#var amaAuthToken = '1AAuth ' + generateToken(nonce, timestamp, saltedPass)
#print("nonceBase64 = ", nonceBase64) #YWdDMjd1WUlCQUxC

uniqueID = generate_uniqueID()


if __name__ == '__main__':
    print('url = ', url)
    
    display_ticket()
    exit()
    
    #QueueList:

    QOffice = 'HANQH05IN'
    QNum = 40
    QCategory = 0
    GdsPos = '1A'
    OfficePos = r'HANQH05IN' # HANQH05IN
    # Neu dung HANQH05I* thi bi loi: <errorCode>91D</errorCode>
    # Office identification. It can contain wildcards ???
    '''
    rlocs, msg = QueueList(QOffice, QNum, QCategory, GdsPos, OfficePos)

    if msg != '':
        print('msg = ', msg)
    else:
        print('rlocs = ', rlocs)
    '''
    
    #rloc = '5M7P28'
    #delayDate, delayTime = '19OCT23', '2300'
    #rloc, session = DelayQueue(rloc, delayDate, delayTime)
    #errorCode 932: PNR PRESENT - PLEASE FINISH OR IGNORE  --> ???
    #exit()
    '''
    rloc, session = StartQueue(QOffice, QNum, QCategory)
    
    #pnr, session, msg = PNR_Retrieve(rloc) #Error: 1753|Application|UNABLE IN QUEUE MODE : khong RT duoc theo rloc
    
    pnr, msg = PNR_Retrieve_Active(session)

    
    print('pnr = ', pnr)
    print('session = ', session)
    exit()
    '''
    QOfficeTo = 'HANQH08AA'
    QNumTo = 11
    QCategoryTo = 0
    
    #Not in queue mode:
    #rloc = 'TCTFW4'
    #rloc = Queue_PlacePNR(rloc, QOfficeTo, QNumTo, QCategoryTo) # QE11C0/HANQH08AA
    #print('rloc = ', rloc)
    #exit()
    '''
    if rloc != '':
        rloc, session = PlaceQueue(rloc, QOfficeTo, QNumTo, QCategoryTo, session) # in queue mode
        #Only return rloc, not pnr!
    
    if rloc != '':
        rloc, session = RemoveQueue(rloc, session)
        #Only return rloc, not pnr!
        
    if rloc != '':
        rloc, session = IgnoreQueue(rloc, session)
        #Only return rloc, not pnr!
    
    # if queue has no item left --> error: ENTRY VALID ONLY FROM QUEUE
    StopQueue(session) # End session here
    exit()
    '''
    
    #QueueMoveItem:
    '''
    fromQOffice, fromQNum, fromQCategory = 'HANQH05IN', 0, 0
    toQOffice, toQNum, toQCategory = 'HANQH0980', 6, 3
    rloc = '5L6OOM' # QGN4JJ 5LLI3O 5L6OOM 5L9JZ2 5LI35K 5LK5TM
    
    bOk, msg = QueueMoveItem(fromQOffice, fromQNum, fromQCategory, toQOffice, toQNum, toQCategory, rloc)
    if msg != '':
        print('msg = ', msg)
    print('bOk = ', bOk)
    '''
    
    #Availability:
    '''
    DepDate = datetime.date.today().strftime("%d%m%y") #'260723' # ddmmyy
    FromCity = 'SGN'
    ToCity = 'HAN'
    
    lines, msg, session = GetAvail(DepDate, FromCity, ToCity)
    if msg != '':
        print('msg = ', msg)
    else:
        for line in lines: print(line)
    '''
    
    # Xac dinh session truoc khi RT PNR!
    
    # PNR Retrieve and Cryptic command:
    '''
    rloc = 'RQTEGO' #5MXZMU 5L6OOM 5MWIEZ # 5MKUMZ 5MHYGK
    pnr, session, msg = PNR_Retrieve(rloc, session)
    if msg != '': #Error
        print('msg = ', msg)
    else:
        print(pnr) 
        print(f'session = {session}')
        
        #cmd = 'he pnr' 'RT 5MWIEZ' 'LP/T/QH289/11AUG': list ticketed pax
        #text, msg = Cryptic(cmd)
        
        cmd = 'ITRD' #IEP : display ELECTRONIC TICKET PASSENGER ITINERARY RECEIPT
        TransactionStatusCode="InSeries"
        text, msg = Cryptic_Sess(cmd, session, TransactionStatusCode)
        if msg != '':
            print('msg = ', msg)
        else:
            print('text = ', text)
            cmd = 'MD'
            while msg == '' and text[-1] == ')': # next page
                session['SeqNumber'] += 1
                text, msg = Cryptic_Sess(cmd, session, TransactionStatusCode)
                if msg != '':
                    print('msg = ', msg)
                else:
                    print('text = ', text)

        #To end session:
        session['SeqNumber'] += 1
        cmd = 'MD'
        TransactionStatusCode = 'End'
        text, msg = Cryptic_Sess(cmd, session, TransactionStatusCode)
        if msg != '':
            print('msg = ', msg)
        else:
            print('text = ', text)
        
    '''
    
    #ListPax:
    '''
    flt = 101
    boardPoint, offPoint = 'HAN', 'DAD'
    year, month, day = 2023, '10', 9
    
    rlocs, msg, session = ListPax(flt, year, month, day, boardPoint, offPoint)
    if msg != '':
        print('msg = ', msg)
    else:
        print('rlocs = ', rlocs)
    
    exit()
    '''
    #GetFlightInven:
    
    flt = 413
    depDate = '141023' # datetime.date.today().strftime("%d%m%y") #'100823' # ddmmyy
    
    legs, msg = GetFlightInven(flt, depDate)
    if msg != '':
        print('msg = ', msg)
    else:
        for leg in legs: 
            print(flt, depDate, leg['depCity'], leg['arrCity'])
            for cabin in leg['cabins']: print(cabin)
    exit()
    
    # PNR_AddMultiElements TST_Display:
    '''
    rloc = 'RQTEGO'
    paxs, msg = PNR_AddMultiElements_TST_Display(rloc)
    if msg != '':
        print('msg = ', msg)
    else:
        for pax in paxs: print(pax)
    '''
    
    # PNR_AddRMK:
    '''
    paxs, msg = PNR_AddRMK(rloc, rmk)
    if msg != '':
        print('msg = ', msg)
    else:
        for pax in paxs: print(pax)
    '''
    
    #PNR_Cancel:
    #PNR_Retrieve to get element number to delete:
    #<faultstring>1931|Application|NO MATCH FOR RECORD LOCATOR</faultstring>
    '''
    rloc = '6TYMZM'
    pnr, session, msg = PNR_Retrieve(rloc)
    print(pnr)
    
    #element = {'identifier': 'OT', 'number': 150} # Other element Tattoo
    element = {'identifier': 'ST', 'number': 8}  # Segment Tattoo
    exit()
    '''
    #if wrong number value --> <faultcode>soap:Server</faultcode><faultstring>1895|Application|CHECK ELEMENT NUMBER</faultstring>
    '''
    number la gia tri sau khi RT PNR, trong 
    <elementManagementData>
        <reference>
            <qualifier>OT</qualifier>
            <number>146</number>
        </reference>
    </elementManagementData>
    
    chu khong phai element number trong pnr tren GUI
    
    or :
    <originDestinationDetails>
        <originDestination></originDestination>
        <itineraryInfo>
            <elementManagementItinerary>
                <reference>
                    <qualifier>ST</qualifier>
                    <number>7</number>
                </reference>
                <segmentName>AIR</segmentName>
                <lineNumber>2</lineNumber>
            </elementManagementItinerary>
            
    </originDestinationDetails>
    '''
    
    '''
    paxs, msg = PNR_Cancel(rloc, element, session)
    if msg != '':
        print('msg = ', msg)
    else:
        for pax in paxs: print(pax)
    '''
    
    '''
    Error:
    <soapenv:Body>
		<soap:Fault
			xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
			<faultcode>soap:Server</faultcode>
			<faultstring>5|Application|CHECK SEGMENT NUMBER</faultstring>
			<faultactor>SI:Backend</faultactor>
		</soap:Fault>
	</soapenv:Body>
    
    '''
    #PNR_Rebook:
    
    '''
    rloc = '5BAWEA' # Group pnr --> <freeText>NOT VALID FOR GROUP PNR</freeText>
    pnr, session, msg = PNR_Retrieve(rloc, session)
    if msg != '': #Error
        print('msg = ', msg)
    else:
        print(pnr) 
        print(f'session = {session}')
        
        #FromSegment = {'FromCity':'HAN','ToCity':'SGN','DepDate': '010923','DepTime':'0535','RBD':'K','Flt':'201','NumPax':1}
        #ToSegment   = {'FromCity':'HAN','ToCity':'SGN','DepDate': '010923','DepTime':'0535','RBD':'Q','Flt':'201','NumPax':1}
        
        FromSegment = {'FromCity':'HAN','ToCity':'SGN','DepDate': '300823','DepTime':'0720','RBD':'M','Flt':'203','NumPax':11}
        ToSegment   = {'FromCity':'HAN','ToCity':'SGN','DepDate': '300823','DepTime':'0720','RBD':'Q','Flt':'203','NumPax':11}
        
        PNR_Rebook(session, FromSegment, ToSegment)
        PNR_Add_ReceivedFrom(session)
    '''
    
    # Group pnr: Cancel and Add Segment:
    rloc = '684CW2' #'5M7MH7' # 9 pax '5BAWEA' # Group pnr 11 pax
    #pnr, session, msg = PNR_Retrieve(rloc, session)
    #print(pnr)
    
    #Add Segment: class Q (khong can RF element va EOT): do it before cancel segment to keep SSR GRPF element not cancelled
    segment = {'FromCity': 'HAN', 'ToCity': 'SGN', 'DepDate': '010923', 'RBD': 'Q', 'Flt':'203', 'NumPax': 11, 'Status': 'SG'}
    #PNR_AddSegment(segment, session) # NUMBER OF PASSENGERS EXCEEDS NINE
    
    #Cancel Segment: class K
    '''
    segment = {'FromCity':'HAN','ToCity':'SGN','DepDate': '010923', 'RBD':'K', 'Carrier': 'QH', 'Flt':'201','NumPax':11, 'Status': 'HN'}
    #QH 201 K 01SEP 5 HANSGN HN11
    qualifier = get_seg_qualifier(pnr['segments'], segment)
    print('qualifier = ', qualifier)
    element = {'identifier': 'ST', 'number': qualifier}  # Segment Tattoo
    
    paxs, msg = PNR_Cancel(rloc, element, session)
    if msg != '':
        print('msg = ', msg)
    else:
        for pax in paxs: print(pax)
    '''
    
    #Add RMK:
    rmk = 'Cancel class M, book class Q'
    #paxs, msg = PNR_AddRMK(rloc, rmk, session)
    
    #Flight Info:
    flt = '219'
    depDate = '271123' # ddmmyy
    #getFlightInfo(session, flt, depDate)