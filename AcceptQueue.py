import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import pyautogui
import time
import imutils
import tkinter
import threading
import riotwatcher
import tkinter as TK
from threading import Thread
import sys
import os

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
    return Screen

#Compare screenshot to passed image template as argument
def TemplateMatch(Template, Template_Height, Template_Width):

    #Take a screenshot
    Screen = Screenshot()
    Found = None
    #loop over scaled versions of screenshot
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        #Resize image
        Resized = imutils.resize(Screen, width = int(Screen.shape[1] * scale))
        Ratio = Screen.shape[1] / float(Resized.shape[1])
        #Make sure scaled image is bigger than template
        if Resized.shape[0] < Template_Height or Resized.shape[1] < Template_Width:
            break
        #Edge template image
        Edged = cv.Canny(Resized, 50, 200)
        #Comapre images using OPENCV
        Result = cv.matchTemplate(Edged, Template, cv.TM_CCOEFF_NORMED)
        #Grab maxVal and compare it until best match is obtained
        (_, maxVal, _, maxLoc) = cv.minMaxLoc(Result)
        if Found is None or maxVal > Found[0]:
            
            print("MaxVal: ", maxVal)
            Found = (maxVal, maxLoc, Ratio)  
    
    #Show image with selection
    #(_, maxLoc, Ratio) = Found
    #(startX, startY) = (int(maxLoc[0] * Ratio), int(maxLoc[1] * Ratio))
    #(endX, endY) = (int((maxLoc[0] + Template_Width) * Ratio), int((maxLoc[1] + Template_Height) * Ratio))
    #cv.rectangle(Screen, (startX, startY), (endX, endY), (0, 0, 255), 2)
    #cv.imshow("Image", Screen)
    #cv.waitKey(0)

    return Found

#Await queue pop and accept
Status = False
def AcceptQueue():
    #Grab accept button image and edge it
    Template = cv.imread(resource_path("AcceptButton.png"), 0)
    Template = cv.Canny(Template, 50, 200)
    (Template_Height, Template_Width) = Template.shape[:2]
    #Look for accept button 
    while Status:
        maxVal, maxLoc, Ratio = TemplateMatch(Template, Template_Height, Template_Width )
        if maxVal >= 0.6:
            #Move mouse and click it
            ClickX = int((maxLoc[0] + (Template_Width/2)) * Ratio)
            ClickY = int((maxLoc[1] + (Template_Height/2)) * Ratio)
            pyautogui.leftClick(ClickX,ClickY, 2, 0)
            time.sleep(3)
        time.sleep(2)
        

def Toggle():
    T = Thread(target= AcceptQueue)
    global Status 
    if Status:
        Button.config(text='OFF')
        Status = False
        
    else:
        Button.config(text='ON')
        Status = True
        T.start()
        

Window = TK.Tk()
Window.geometry("200x25")
Window.resizable(False,False)
Window.title("AQ")
Button = TK.Button(text="OFF", width=10, command=Toggle)
Label = TK.Label(text= "Accept Queues")
Label.pack(side= TK.LEFT)
Button.pack(side = TK.RIGHT)
Window.mainloop()





