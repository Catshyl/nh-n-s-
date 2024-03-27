import time
import pyautogui as pa

pa.click(123, 14)
time.sleep(0.01)
pa.keyDown('alt'); pa.press('2'); pa.keyUp('alt') # menu Inventory Management
time.sleep(0.01)
pa.press('enter')