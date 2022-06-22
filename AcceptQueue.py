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
    return Screen

#Compare screenshot to passed image template as argument
def TemplateMatch(Template, Template_Height, Template_Width):

    #Take a screenshot
    Screen = Screenshot()
    Found = None
    #loop over scaled versions of screenshot
    for scale in np.linspace(0.1, 1, 35)[::-1]:
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
            
            print("MaxVal: ", maxVal, "  Ratio: ",scale)
            Found = (maxVal, maxLoc, Ratio)  
    
    #Show image with selection
    #(_, maxLoc, Ratio) = Found
    #(startX, startY) = (int(maxLoc[0] * Ratio), int(maxLoc[1] * Ratio))
    #(endX, endY) = (int((maxLoc[0] + Template_Width) * Ratio ), int((maxLoc[1] + Template_Height)* Ratio)) 
    #cv.rectangle(Screen, (startX, startY), (endX, endY), (0, 0, 255), 2)
    #cv.imshow("Edged", Screen)
    #cv.waitKey(0)
    return Found

#Await queue pop and accept
def AcceptQueue():
    (Template_Height, Template_Width) = Template.shape[:2]
    #Look for accept button 
    while Running:
        maxVal, maxLoc, Ratio = TemplateMatch(Template, Template_Height, Template_Width )
        if maxVal >= 0.6:
            #Move mouse and click it
            ClickX = int((maxLoc[0] + (Template_Width/2)) * Ratio)
            ClickY = int((maxLoc[1] + (Template_Height/2)) * Ratio)
            pyautogui.leftClick(ClickX,ClickY, 2, 0)
            time.sleep(3)
        time.sleep(2)
        
#On Off Button
Running = False
def Toggle():
    T = Thread(target= AcceptQueue, daemon= True)
    global Running
    #Grab accept button image and edge it
    global Template 
    Path = "AcceptButton"+ResButton["text"]+".png"
    Template= cv.imread(resource_path(Path), 0)
    Template = cv.Canny(Template, 50, 200)

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
    
    #Change resolution of image and change button text to match
    if ResButton["text"] == "1024x576":
        ResButton.config(text = "1280x720")

    elif ResButton["text"] == "1280x720":
        ResButton.config(text = "1600x900")
        
    else:
        ResButton.config(text = "1024x576")
        


#GUI Stuff
Window = TK.Tk()
Window.geometry("210x53")
Window.resizable(False,False)
Window.title("AQ")
ToggleLabel = TK.Label(text= "Accept Queues")
ToggleLabel.grid(row = 0, column = 0)
ToggleButton = TK.Button(text="OFF", width=10, command=Toggle)
ToggleButton.grid(row = 0, column = 1)
ResLabel = TK.Label(text= "Client Resolution")
ResLabel.grid(row = 1, column = 0)
ResButton = TK.Button(text="1024x576", width=10, command=ChangeRes)
ResButton.grid(row = 1, column = 1, padx= 35)
Window.mainloop()





