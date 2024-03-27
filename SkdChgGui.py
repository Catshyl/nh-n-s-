import datetime
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import filedialog
#from os import path
from threading import Thread
import pyautogui as pa

import config  # import global variables
import run
import convert
import SendSkdMsg

about_msg = 'by Trần Đại Long + Lê Ngọc Anh\nLast updated on 31-Jul-2023'

fullFileName = ''

'''
def sel():
   selection = "You selected the option " + str(var_env.get())
   print(selection)
'''

def OpenFile_click():
    global fullFileName
    #initial_dir = path.dirname(__file__)
    initial_dir = 'C:/Temp'
    fullFileName = filedialog.askopenfilename(initialdir=initial_dir,
                    filetypes=[("Excel files", ".xlsx"), ("Excel 97 files", ".xls")])
    entFileName.delete(0, END)
    entFileName.insert(0, fullFileName)

    config.bStop = False
    btnRunSC["state"] = "enable"
    btnStop["state"] = "disabled"


#  Buttons on fr_buttons1:
def scanning_sc():
    global fullFileName # = "Input.xlsx"
    if fullFileName is not None:        
        bStaging = (var_env.get() == 1)
        #print('bStaging = ', bStaging)
        bKHDB_Format = (var_file_format.get() == 1)
        
        run.RunSC(bKHDB_Format, fullFileName, bStaging)
        messagebox.showinfo('Schedule Change', 'Finished at ' + datetime.datetime.now().strftime('%H:%M:%S'))


def start_thread_sc():
    btnRunSC["state"] = "disabled"
    btnStop["state"] = "enable"
    config.bStop = False

    # Create and launch a thread
    t = Thread(target=scanning_sc)
    t.start()


def scanning_convert():
    global fullFileName
    if fullFileName is not None:
        outFileName, asm_msgList, ssm_msgList = convert.convert_file(fullFileName)
        
        bStaging = (var_env.get() == 1)
        SendSkdMsg.SendSkd(bStaging, asm_msgList, ssm_msgList)
        
        messagebox.showinfo('Convert', 'Finished at ' + datetime.datetime.now().strftime('%H:%M:%S'))


def start_thread_convert():
    btnConvert["state"] = "disabled"
    btnStop["state"] = "enable"
    config.bStop = False

    # Create and launch a thread
    t = Thread(target=scanning_convert)
    t.start()  


def btnStop_click():
    config.bStop = True
    btnRunSC["state"] = "enable"
    btnConvert["state"] = "enable"
    btnStop["state"] = "disabled"
    

def btnExit_click():
    window.destroy()


def btnAbout_click():
    messagebox.showinfo('Auto SC', about_msg)
           
    
def CreateSkdChgGui():
    global window, var_env, var_file_format
    
    window = Tk() # Toplevel(login_screen)

    window.title("Bamboo Airways Auto SC")
    scr_size = pa.size()
    left_pos = scr_size[0] - (360+30)
    top_pos = scr_size[1] - (100+120)
    win_geometry = '360x160+' + str(left_pos) + '+' + str(top_pos) # '360x160+1000+560'
    window.geometry(win_geometry) # "window width x window height + position right + position down"
    # window.rowconfigure(0, minsize=800, weight=1)
    #window.columnconfigure(0, minsize=20, weight=1)

    fr_env = Frame(window)
    fr_env.grid(row=0, column=0, sticky="ns", pady=3)
                      
    fr_file = Frame(window)
    fr_file.grid(row=1, column=0, sticky="ns", pady=3)
    
    fr_file_format = Frame(window)
    fr_file_format.grid(row=2, column=0, sticky="ns", pady=3)
    
    fr_buttons1 = Frame(window)
    fr_buttons1.grid(row=3, column=0, sticky="ns", pady=3)
    #mainframe.columnconfigure((0,1), weight=1, pad=5)

    fr_buttons2 = Frame(window)
    fr_buttons2.grid(row=4, column=0, sticky="ns", pady=3)
    
    # Items on fr_env:
    lblEnv_style = Style() # style for Label Env: 'Env.TLabel' la style name
    lblEnv_style.configure('Env.TLabel', foreground='blue', background='light green', font = ("arial", 11))    
    lblEnv = Label(fr_env, text='Environment:', style='Env.TLabel')
    lblEnv.grid(row=0, column=0)

    var_env = IntVar(None, 2) # default to Production
    # Style class to add style to Radiobutton. It can be used to style any ttk widget
    style_staging = Style(fr_env)
    style_staging.configure("staging.TRadiobutton", background = "orange", foreground = "black", font = ("arial", 10, "bold")) 
    r_staging = Radiobutton(fr_env, text="Staging", variable = var_env, value = 1, style='staging.TRadiobutton')
    r_staging.grid(row=0, column=1)
    
    style_production = Style(fr_env)
    style_production.configure("production.TRadiobutton", background = "light green", foreground = "red", font = ("arial", 10, "bold"))
    r_production = Radiobutton(fr_env, text="Production", variable = var_env, value = 2, style='production.TRadiobutton')
    r_production.grid(row=0, column=2)
    
    btnOpenFile = Button(fr_file, text="Open File", command=OpenFile_click)
    btnOpenFile.grid(row=0, column=0, padx=5)
    
    global entFileName
    entFileName = Entry(fr_file, width=40) # textbox
    entFileName.grid(row=0, column=1)
   
    var_file_format = IntVar(None, 1) # default to KHDB
    global radOCC_Format
    radOCC_Format = Radiobutton(fr_file_format, text="OCC format", variable = var_file_format, value = 0, style='staging.TRadiobutton')
    radOCC_Format.grid(row=0, column=0)

    radKHDB_Format = Radiobutton(fr_file_format, text="KHDB format", variable = var_file_format, value = 1, style='production.TRadiobutton')
    radKHDB_Format.grid(row=0, column=1)    
   
    btnConvert_style = Style() # style for button2    
    btnConvert_style.configure('Convert.TButton', foreground='purple', background='light green', font = ("arial", 10, "bold"))
    
    global btnConvert
    btnConvert = Button(fr_buttons1, text="Convert", command=start_thread_convert, style='Convert.TButton')
    btnConvert.grid(row=0, column=0, padx=5)
   
    btnRunSC_style = Style() # style for button2    
    btnRunSC_style.configure('RunSC.TButton', foreground='blue', background='light green', font = ("arial", 10, "bold"))
    
    global btnRunSC
    btnRunSC = Button(fr_buttons1, text="SC", command=start_thread_sc, style = 'RunSC.TButton')
    btnRunSC.grid(row=0, column=1)
             
    btnStop_style = Style() # style for button2    
    btnStop_style.configure('Stop.TButton', foreground='red', background='yellow', font = ("arial", 10, "bold"))
    
    global btnStop
    btnStop = Button(fr_buttons2, text="Stop", command=btnStop_click, style='Stop.TButton')
    btnStop.grid(row=0, column=0)
    
    btnExit = Button(fr_buttons2, text="Exit", command=btnExit_click)
    btnExit.grid(row=0, column=1)

    btnAbout = Button(fr_buttons2, text="About", command=btnAbout_click)
    btnAbout.grid(row=0, column=2)    

    window.mainloop()

if __name__ == '__main__':   
    CreateSkdChgGui()
