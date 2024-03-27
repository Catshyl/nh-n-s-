import datetime
import pyautogui as pa
import numpy as np
import cv2
#import pytesseract
from PIL import Image
import logging
import pytz


def isNaN(num):
    return num != num
    
    
def UTC2LocalTime(date_UTC, airport, df_utc):
    #Input: dptDate_UTC co kieu datetime la ngay gio UTC tai airport
    #   airport, df_utc
    #Output: ngay gio LT tai airport
    
    # time: https://time.is/Berlin
    #local_timezone = pytz.timezone('Asia/Kolkata')
    
    #logStr = 'UTC2LocalTime'
    #print(logStr)
    #logging.warning(logStr)
    
    #Tim airport trong bang tblTimezone
    if airport in df_utc.index:
        TimeZone = df_utc.loc[airport, 'TimeZone']
        region = df_utc.loc[airport, 'Region']
        time_zone_city = df_utc.loc[airport, 'TimeZoneCity']
        #print('airport, region, time_zone_city = ', airport, region, time_zone_city)
        local_timezone = pytz.timezone(f'{region}/{time_zone_city}')
        
        if TimeZone == float('inf'):
            #date_LT = pytz.utc.localize(date_UTC, is_dst=None).astimezone(local_timezone)
            date_LT = local_timezone.fromutc(date_UTC)
        else:
            date_LT = date_UTC + datetime.timedelta(hours=int(TimeZone))
            date_LT = date_LT.replace(tzinfo=local_timezone)
    else:
        logStr = f'Cannot find airport {airport} in table tblTimeZone!'
        raise Exception(logStr)
        
    return date_LT
    
    
def LocalTime2UTC(date_obj, timezone):
    #Input : date_obj co kieu datetime
    #        timezone co kieu float

    return date_obj + datetime.timedelta(hours=-timezone)


def date2str(date_obj):
    #Input : date_obj co kieu datetime
    return date_obj.strftime("%d-%b-%Y") #'28-Jun-2021'


def date2str2(date_obj):
    #Input : date_obj co kieu datetime
    return date_obj.strftime("%d%b%y").upper() #'28Jun21'
    
    
def str2date(date_str):
    #date_str co dang dd-mmm-yyyy
    #return 1 date object
    return datetime.datetime.strptime(date_str, '%d-%b-%Y').date()


def add_day(date_str, numday):    
    #date_str co dang dd-mmm-yyyy
    #return 1 str dang dd-mmm-yyyy
    
    if numday != 0:        
        dateObj = str2date(date_str) + datetime.timedelta(days=numday)
        output = dateObj.strftime("%d-%b-%Y")  #'28-Jun-2021'
    else:
        output = date_str
    return output


def add_day2(indate, numday):    
    #indate co kieu date
    #return kieu date
    
    if numday == 0:
        return indate
        
    return indate + datetime.timedelta(days=numday)


def day_diff(date1, date2):    
    # input: date1, date2 co cung kieu date or datetime
    # output: so ngay giua date1 - date2
    return int((date1 - date2) / datetime.timedelta(days=1))


def weekday(date_str):
    #date_str co dang dd-mmm-yyyy
    dateObj = str2date(date_str)
    # return weekday from 1 (Monday) to 7 (Sunday)
    return str(dateObj.weekday() + 1) 


def weekday2(date_obj):
    #date_obj co kieu date
    # return weekday from 1 (Monday) to 7 (Sunday)
    return str(date_obj.weekday() + 1) 


def now_plus_24h():
    tdy = datetime.datetime.today()
    return tdy + datetime.timedelta(days=1)


def depDateTime_after_now_plus_24h(dptDate, depTime):
    date_time_str = dptDate + ' ' + depTime
    dptDateObj = datetime.datetime.strptime(date_time_str, '%d-%b-%Y %H:%M')
    return dptDateObj > now_plus_24h()
        
        
def create_log():
    logFileName = 'C:/Data/Log/' + datetime.datetime.now().strftime("%d-%b-%Y") + '.txt' # dd-mmm-yyyy        
    logging.basicConfig(filename=logFileName, filemode='a',
                        format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.INFO) # append

'''
def get_region(win):
	#Input: win la 1 tuple dang:
        #Live_Flights_Win = ('imgs/Live_Flights_Win.jpg', (291, 131), (370, 150), 'Live Flights') 
        # win[4] = True : cua so nam giua man hinh
	#Output: 
        # bien doi toa do left, top theo do phan giai man hinh hien tai
        # return 1 rectangle dang (left, top, width, heigh)	
    
    left, top = win[1] # vi tri cua chu tren window
    right, bot = win[2]
    left_top = convert_res((left-10, top-10), win)
    return (*left_top, right-left+30, bot-top+30) # increase padding 10 pixels

    
def get_region_no_convert_res(win):
	#Input: win la 1 tuple dang:
        #Live_Flights_Win = ('imgs/Live_Flights_Win.jpg', (291, 131), (370, 150), 'Live Flights') 
	#Output: 1 rectangle dang (left, top, width, heigh)	
    
    left, top = win[1] # vi tri cua chu tren window
    right, bot = win[2]
    return (left-10, top-10, right-left+30, bot-top+30) # increase padding 10 pixels
'''
	
def filter_func(char):
    #return only ascii char
    #return char == '\n' or 32 <= ord(char) <= 126
    return 32 <= ord(char) <= 126


def pre_processing(image):
    #This function take one argument as input. this function will convert input image to binary image
	# image is a numpy array of type uint8
	
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #gray_image = cv2.cvtColor(np.float32(image), cv2.COLOR_BGR2GRAY)
    #gray_image = cv2.cvtColor(np.float32(image), cv2.COLOR_RGB2GRAY)
    # converting it to binary image
    threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return threshold_img
    

def parse_text(threshold_img):
    """
    This function take one argument as input. this function will feed input image to tesseract to predict text.
    Tesseract installer for Windows:
    https://github.com/UB-Mannheim/tesseract/wiki
    https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20201127.exe
    """
    # configuring parameters for tesseract
    #pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    #add to system path: C:\Program Files\Tesseract-OCR\
    
    tesseract_config = r'--oem 3 --psm 6'
    #details = pytesseract.image_to_data(threshold_img, output_type=pytesseract.Output.DICT,
    #                                    config=tesseract_config, lang='eng')
                                        
    #print(pytesseract.image_to_string(Image.open('Train/TR_1.jpg')))
    txt = pytesseract.image_to_string(threshold_img)
    return txt

    
def get_text(left_top, right_bottom):
	#Input: left_top, right_bottom la cac tuple luu vi tri lay anh
	#Output: chup man hinh --> extract pixel at left_top, right_bottom --> convert to text
	
    scr = pa.screenshot() # scr: pillow image co shape row, column
    pix = np.array(scr)[left_top[1]:right_bottom[1], left_top[0]:right_bottom[0], :]
    #img = Image.fromarray(pix)
    #img.save('test.jpg')
    # calling pre_processing function to perform pre-processing on input image.
    thresholds_image = pre_processing(pix)
    # calling parse_text function to get text from image by Tesseract.
    parsed_data = parse_text(thresholds_image)

    txt = ''.join(filter(filter_func, parsed_data.strip()))
    return txt
    

'''
def convert_res(point, win):
    #Input: 
        # point: có dạng (x, y): là 1 điểm trên màn hình có độ phân giải 1366*768
        # win: cua so tren man hinh co do phan giai 1366 x 768
        # win[4] = True neu cua so can giua man hinh
        
    #Output: point có dạng (x, y): là 1 điểm trên màn hình có độ phân giải bất kỳ
    
    # Cac point trong phan mem deu tinh theo do phan giai 1366 * 768:
    if scr_size == (1366, 768) or scr_size == (1360, 768):
        return point
    
    win_point = win[1] # toa do left, top cua win
    if win[4]: # cua so kich thuoc thay doi va can giua man hinh
        box = pa.locateOnScreen(win[0], grayscale=True,confidence=0.9)
        if box is None:
            x = int(point[0] / 1366 * scr_size[0]) # xem lai!
            y = int(point[1] / 768 * scr_size[1])
        else:
            x = int(point[0] - win_point[0] + box[0])
            y = int(point[1] - win_point[1] + box[1])
    else: # cua so kich thuoc co dinh va khong can giua man hinh
        delta_win_left = round((scr_size[0] - 1366) / 2)
        delta_win_top =  round((scr_size[1] - 768) / 2)    
        delta_x = point[0] - win_point[0]
        delta_y = point[1] - win_point[1]
        
        x = win_point[0] + delta_win_left + delta_x
        y = win_point[1] + delta_win_top + delta_y
    return (x, y)
'''    

'''
def locate(win, confidence=0.1):
	#Input: win, confidence
	#Output: position box of win on screen
	
	template = cv2.imread(win[0]) # numpy array: heigh, width
	template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) # BGR
	#template = cv2.Canny(template, 50, 200) #detect edges: neu dung thi co the nhan sai
	(tH, tW) = template.shape[:2]

	#print('tH, tW = ', tH, tW)
	left_top = win[1] # vi tri cua chu tren window
	right_bot = win[2]
	rec = *left_top, right_bot[0]-left_top[0], right_bot[1]-left_top[1]

	image = pa.screenshot(region=rec) #Pil.Image (width, heigh) , RGB
	pix = np.array(image) # (531, 714, 3) # heigh * width
	#print('pix.shape = ', pix.shape)

	gray = cv2.cvtColor(pix, cv2.COLOR_RGB2GRAY) # (531, 714) --> heigh * width
	found = None
	# loop over the scales of the image
	for scale in np.linspace(0.2, 1.0, 20)[::-1]: # scale in descending order
		#scale runs from 1 to 0.2, 20 values
		# resize the big image according to the scale, and keep track of the ratio of the resizing
		#resized = imutils.resize(gray, width = int(gray.shape[1] * scale)) # resized <= gray
		resized = cv2.resize(gray, (int(gray.shape[1] * scale), tH)) # resized <= gray: only resize width
		r = gray.shape[1] / float(resized.shape[1]) # 1.146067415730337
		# if the resized image is smaller than the template, then break from the loop
		if resized.shape[0] < tH or resized.shape[1] < tW:
			break

		# detect edges in the resized, grayscale image and apply template
		# matching to find the template in the image
		#edged = cv2.Canny(resized, 50, 200) # detect edges : co the nham lan: false positive
		edged = resized
		method = cv2.TM_CCOEFF_NORMED #cv2.TM_SQDIFF_NORMED
		
		#pa.locateOnScreen(template, edged, confidence=0.9) su dung:
		#result = cv2.matchTemplate(haystackImage, needleImage, cv2.TM_CCOEFF_NORMED)
		
		#result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
		#result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF_NORMED) # maxVal = 0.14
		#result = cv2.matchTemplate(edged, template, cv2.TM_CCORR_NORMED) # maxVal = 0.372963
		result = cv2.matchTemplate(edged, template, method) # maxVal = 1
		
		(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)		
#https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html
		# If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
		
		if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
			top_left = minLoc
		else:
			top_left = maxLoc
		bottom_right = (top_left[0] + tW, top_left[1] + tH)
				
		#if we have found a new maximum correlation value, then update the bookkeeping variable
		if maxVal >= confidence:
			if found is None or maxVal > found[0]:
				found = (maxVal, top_left, r, edged)
				
		#break # no need to scale bigger image
		
	if found:
		# unpack the bookkeeping variable and compute the (x, y) coordinates
		# of the bounding box based on the resized ratio
		(maxVal, top_left, r, edged) = found
		#print('maxVal = ', maxVal) #
		#print('r = ', r) # r =  
		
		(startX, startY) = (int(top_left[0] * r), int(top_left[1] * r))
		(endX, endY) = (int((top_left[0] + tW) * r), int((top_left[1] + tH) * r))
		#(endX, endY) = (int((top_left[0] + tW) * r), (top_left[1] + tH + 10))
		box = [startX, startY, endX-startX, endY-startY]
		box[0] += win[1][0] # adjust to win position
		box[1] += win[1][1]
	else:
		box = None
		
	return box
		
'''
	
if __name__ == '__main__':
    # reimport library:
    '''	
    from importlib import reload
    reload(mylib)

    mydate = str2date('28-Jun-2021')
    print(mydate)
    print(type(mydate))

    print(add_day('28-Jun-2021', 3))
    
    # Check a cell null:  pd.isnull(df.loc[0, 'IFA'])
    '''
	
    txt = get_text((498, 190), (670, 210) )
    print(txt)

	

#pa.screenshot().getpixel(pa.position())
#unload module:
#from importlib import reload 
#import foo 
#foo = reload(foo)

scr_size = pa.size()