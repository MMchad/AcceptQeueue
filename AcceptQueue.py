from cgi import test
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import pyautogui
import time
import imutils
import tkinter as TK
from threading import Thread
import sys
import os

#Returns actual path for files after release
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#Returns screenshot of screen
def Screenshot():
    Screen = pyautogui.screenshot()
    Screen = cv.cvtColor(np.array(Screen), cv.COLOR_BGR2GRAY)
    Edged = cv.Canny(Screen, 50, 200)
    return Edged

#Compare screenshot to passed image template as argument
def TemplateMatch():

    #Take a screenshot
    Screen = Screenshot()
    Found = None
    global Templates
    for Template in Templates:

        #Comapre templates with screenshot using OPENCV
        Result = cv.matchTemplate(Screen, Template, cv.TM_CCOEFF_NORMED)
        (_, maxVal, _, maxLoc) = cv.minMaxLoc(Result)
        if maxVal > 0.7:
            (TemplateHeight, TemplateWidth) = Template.shape[:2]
            return maxVal, maxLoc, TemplateHeight, TemplateWidth
    return 0,0,0,0
#Await queue pop and accept
def AcceptQueue():
    #Look for accept button 
    while Running:
        maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch()
        if maxVal >= 0.6:
            #Move mouse and click it
            ClickX = int((maxLoc[0] + (TemplateWidth/2)))
            ClickY = int((maxLoc[1] + (TemplateHeight/2)))
            pyautogui.leftClick(ClickX,ClickY, 2, 0)
        time.sleep(0.5)
        
#On Off Button
Running = False
def Toggle():
    T = Thread(target= AcceptQueue, daemon= True)
    global Running
    #Toggle search and change text on button
    if Running:
        ToggleButton.config(text='OFF')
        Running = False
        
    else:
        ToggleButton.config(text='ON')
        Running = True
        T.start()

#Change resolution of image
def ChangeRes():

    #Stop searching
    global Running
    Running = False
    ToggleButton.config(text='OFF')
        

Temp1Path = "AcceptButton1024x576.png"
Temp1 = cv.imread(resource_path(Temp1Path), 0)
Temp1 = cv.Canny(Temp1, 50, 200)

Temp2Path = "AcceptButton1280x720.png"
Temp2 = cv.imread(resource_path(Temp2Path), 0)
Temp2 = cv.Canny(Temp2, 50, 200)

Temp3Path = "AcceptButton1600x900.png"
Temp3 = cv.imread(resource_path(Temp3Path), 0)
Temp3 = cv.Canny(Temp3, 50, 200)

Templates = [Temp1, Temp2, Temp3]

#GUI Stuff
Window = TK.Tk()
Window.geometry("165x25")
Window.resizable(False,False)
Window.title("AQ")
ToggleLabel = TK.Label(text= "Accept Queues")
ToggleLabel.grid(row = 0, column = 0)
ToggleButton = TK.Button(text="OFF", width=10, command=Toggle)
ToggleButton.grid(row = 0, column = 1)
Window.mainloop()





