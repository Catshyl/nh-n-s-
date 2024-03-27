'''
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pywin32
pip install pywin32-301-cp39-cp39-win_amd64.whl

2nd number is ID of cursor type
On Windows 10:
	
    APPSTARTING  handle =  65561
    ARROW  handle =  65539  - normal (xlNorthwestArrow)
    CROSS  handle =  65545
    HAND  handle =  65567 (hand pointer)
    HELP  handle =  65563
    IBEAM  handle =  65541 (xlIBeam)
    ICON  handle =  0
    NO  handle =  65559
    SIZE  handle =  0
    SIZEALL  handle =  65557
    SIZENESW  handle =  65551
    SIZENS  handle =  65555
    SIZENWSE  handle =  65549
    SIZEWE  handle =  65553
    UPARROW  handle =  65547
    WAIT  handle =  65543    # spinning/wait cursor
    xlDefault = 1056704799
'''

'''
import win32gui
import time

for i in range(20):	
	print(win32gui.GetCursorInfo())
	time.sleep(2)
'''
# https://stackoverflow.com/questions/59608898/how-to-get-the-state-of-the-cursor
from win32con import IDC_APPSTARTING, IDC_ARROW, IDC_CROSS, IDC_HAND, \
    IDC_HELP, IDC_IBEAM, IDC_ICON, IDC_NO, IDC_SIZE, IDC_SIZEALL, \
    IDC_SIZENESW, IDC_SIZENS, IDC_SIZENWSE, IDC_SIZEWE, IDC_UPARROW, IDC_WAIT

from win32gui import LoadCursor, GetCursorInfo
import time

def get_current_cursor():
    curr_cursor_handle = GetCursorInfo()[1] 
    # (1, 65539, (303, 556)) 
    # flags, hcursor, (x,y)
    # flags: 0: The cursor is hidden; 1: The cursor is showing; 2: Windows 8: The cursor is suppressed. This flag indicates that the system is not drawing the cursor because the user is providing input through touch or pen instead of the mouse
    # hcursor: cursor handle
    # x, y: cursor position
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-cursorinfo
    
    return Cursor.from_handle(curr_cursor_handle)


class Cursor(object):
    @classmethod
    def from_handle(cls, handle):
        for cursor in DEFAULT_CURSORS:
            if cursor[1].handle == handle:
                return cursor[0] #DEFAULT_CURSORS.index(cursor) , Cursor.__init__
                # return name of cursor handle: APPSTARTING, ARROW, CROSS, ...
        return cls(handle=handle)

    def __init__(self, cursor_type=None, handle=None):
        if handle is None:
            handle = LoadCursor(0, cursor_type)
        self.type = cursor_type
        self.handle = handle


DEFAULT_CURSORS = (
    ('APPSTARTING', Cursor(IDC_APPSTARTING)), \
    ('ARROW', Cursor(IDC_ARROW)), \
    ('CROSS', Cursor(IDC_CROSS)), \
    ('HAND', Cursor(IDC_HAND)), \
    ('HELP', Cursor(IDC_HELP)), \
    ('IBEAM', Cursor(IDC_IBEAM)), \
    ('ICON', Cursor(IDC_ICON)), \
    ('NO', Cursor(IDC_NO)), \
    ('SIZE', Cursor(IDC_SIZE)), \
    ('SIZEALL', Cursor(IDC_SIZEALL)), \
    ('SIZENESW', Cursor(IDC_SIZENESW)), \
    ('SIZENS', Cursor(IDC_SIZENS)), \
    ('SIZENWSE',Cursor(IDC_SIZENWSE)), \
    ('SIZEWE', Cursor(IDC_SIZEWE)), \
    ('UPARROW', Cursor(IDC_UPARROW)), \
    ('WAIT', Cursor(IDC_WAIT)))


def wait_cursor(cursor_name, timeout, period=0.2):
    #Input: cursor_name
    #Output: wait until cursor_name appear on screen, or timeout
    
    mustend = time.time() + timeout
    while time.time() < mustend:
        time.sleep(period)

        if get_current_cursor() == cursor_name:
            time.sleep(2) # wait 2 seconds more
            return

    raise Exception('Error: timeout while waiting cursor ' + cursor_name + ' appear!')


if __name__ == '__main__':
    for cursor in DEFAULT_CURSORS:
        print(cursor[0], ' handle = ', cursor[1].handle)
        
    #while(True):
    #    print(get_current_cursor())	
    #    time.sleep(1)