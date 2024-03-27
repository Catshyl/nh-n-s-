import win32api,win32con

bStop = False
window_title_pos = (113, 13) # to click vao ung dung Inventory cua 1A

#selected_row_color = (255, 200, 200)

#although we import config many times but print Hello 1 time only
#print('Hello') 

def turn_off_key(key):
    if win32api.GetKeyState(key) == 1:
        win32api.keybd_event(key, 0) # 0: turn off; 1: turn on
        # win32api.mouse_event()
        
    
def turn_off_capslock_numlock_key():
    # Turn off CapsLock, NumLock and ScrollLock keyboards:
    
    turn_off_key(win32con.VK_CAPITAL) # CapsLock
    turn_off_key(win32con.VK_NUMLOCK) # NumLock
    #turn_off_key(win32con.VK_SCROLL) # ScrollLock ? not Work ?
    
    