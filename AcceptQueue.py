from multiprocessing import Process
from tokenize import String
import cv2 as cv
from cv2 import waitKey
import numpy as np
import pyautogui
import time
import tkinter as TK
from threading import Thread
import sys
import os

from setuptools import Command

#Returns actual path for files after release
def Path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#Move mouse and click it
def Click(X, Y, Height, Width):
    ClickX = int((X + (Width/2)))
    ClickY = int((Y + (Height/2)))
    pyautogui.leftClick(ClickX,ClickY, 2, 0)

#Returns screenshot of screen
def Screenshot():
    Screen = pyautogui.screenshot()
    Screen = cv.cvtColor(np.array(Screen),cv.COLOR_RGB2BGR)
    return Screen

#Compare screenshot to passed image template as argument
def TemplateMatch(Templates, Canny):

    #Take a screenshot
    Screen = Screenshot()
    if Canny:
        Screen = cv.Canny(Screen, 50, 200)
    for Template in Templates:
        if Canny:
            Template = cv.Canny(Template, 50, 200)
        #Comapre templates with screenshot using OPENCV
        Result = cv.matchTemplate(Screen, Template, cv.TM_CCOEFF_NORMED)
        (_, maxVal, _, maxLoc) = cv.minMaxLoc(Result)
        #print(maxVal)
        if maxVal > 0.7:
            (TemplateHeight, TemplateWidth) = Template.shape[:2]
            return maxVal, maxLoc, TemplateHeight, TemplateWidth
    return 0,0,0,0

#Await queue pop and accept
def AcceptQueue():
    global AcceptButtons,AutoAccept
    #Look for accept button 
    while True and AutoAccept:

        maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(AcceptButtons, False)
        if maxVal >= 0.75:
            Click(maxLoc[0], maxLoc[1], TemplateHeight, TemplateWidth)
            time.sleep(4)
        time.sleep(2)

    
def ChampSelect():
    global ChampToSelect, InChampSelect, ChampToBan
    maxVal = 0

    if InChampSelect:
        while maxVal < 0.75 and InChampSelect and AutoSelect:
            maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(BanButton, True)
            time.sleep(2)
        maxVal = 0
        if InChampSelect:
            BanChamp(ChampToBan)
        while maxVal < 0.75 and InChampSelect and AutoSelect:
            maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(SearchBar, False)
            time.sleep(2)
        if InChampSelect and AutoSelect:
            SearchForChamp(ChampToSelect)
            time.sleep(0.1)
            SelectChamp()
            LockInChamp()
            
def LockInChamp():
    global LockIn
    maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(LockInButton, True)
    if maxVal > 0.75 and AutoSelect:
        Click(maxLoc[0], maxLoc[1], TemplateHeight, TemplateWidth)

def BanChamp(ChampToBan):

    global BanButton
    SearchForChamp(ChampToBan)
    time.sleep(0.1)
    SelectChamp()
    maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(BanButton, True)
    if maxVal >= 0.75 and AutoSelect:
        Click(maxLoc[0], maxLoc[1], TemplateHeight, TemplateWidth)
    

def SearchForChamp(ChampName):

    global SearchBar1
    maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(SearchBar, False)
    if maxVal > 0.75 and AutoSelect:   
         Click(maxLoc[0], maxLoc[1], TemplateHeight, TemplateWidth)
         pyautogui.write(ChampName)
    return maxVal

def SelectChamp():
    global TopLane
    maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(TopLane, False)
    if maxVal >= 0.75:

        Click(maxLoc[0] + 25 , maxLoc[1] + 50, TemplateHeight, TemplateWidth)
    
def DodgeCheck():
    global InChampSelect, DodgeChecks, AutoSelect
    while True and AutoSelect:
        while InChampSelect and AutoSelect:
            maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(DodgeChecks, True)
            print(maxVal)
            if maxVal >= 0.75:
                InChampSelect = False
            time.sleep(5)
        time.sleep(5)

def CheckChampSelect():
    global SearchBar1, InChampSelect, AutoSelect

    while True and AutoSelect:
        while not InChampSelect and AutoSelect:
            print("SELECT")
            maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(SearchBar, False)
            if maxVal >= 0.75:
                InChampSelect = True
                ChampSelectThread = Thread(target = ChampSelect, daemon = True)
                ChampSelectThread.start()
                ChampSelectThread.join(timeout = 150)
                InChampSelect = False
            if not InChampSelect:
                time.sleep(5)



InChampSelect = False
def Procedure():
    CheckChampSelectThread = Thread(target = CheckChampSelect, daemon = True)
    DodgeCheckThread = Thread(target= DodgeCheck, daemon = True)
    CheckChampSelectThread.start()
    DodgeCheckThread.start()


#On Off Buttons
AutoSelect = False
def ToggleAutoSelect():
    global AutoSelect, ToggleSelectButton, ChampBanText, ChampSelectText,ChampToBan,ChampToSelect
    print(ChampToBan,ChampToSelect)
    ProcedureThread = Thread(target = Procedure, daemon= True)
    #Toggle search and change text on button
    if AutoSelect:
        ToggleSelectButton.config(text='OFF')
        ChampBanText.config(state = TK.NORMAL, bg = "white")
        ChampSelectText.config(state = TK.NORMAL, bg = "white")
        AutoSelect = False
        
    else:
        ToggleSelectButton.config(text='ON')
        ChampBanText.config(state = TK.DISABLED, bg = "gray")
        ChampSelectText.config(state = TK.DISABLED, bg = "gray")
        AutoSelect = True
        ProcedureThread.start()
        
AutoAccept = False
def ToggleAccept():
    global AutoAccept,ToggleAcceptButton
    print(ChampToBan)
    AcceptQueueThread = Thread(target = AcceptQueue, daemon= True)
    #Toggle search and change text on button
    if AutoAccept:
        ToggleAcceptButton.config(text='OFF')
        AutoAccept = False
        
    else:
        ToggleAcceptButton.config(text='ON')
        AutoAccept = True
        AcceptQueueThread.start()

def UpdateChampToSelect(Name):
    global ChampToSelect
    ChampToSelect = Name.get()

def UpdateChampToBan(Name):
    global ChampToBan
    ChampToBan = Name.get()



AcceptButton1Path = "AcceptButton1024x576.png"
AcceptButton1 = cv.imread(Path(AcceptButton1Path), 0)
AcceptButton1 = cv.cvtColor(np.array(AcceptButton1),cv.COLOR_RGB2BGR)

AcceptButton2Path = "AcceptButton1280x720.png"
AcceptButton2 = cv.imread(Path(AcceptButton2Path), 0)
AcceptButton2 = cv.cvtColor(np.array(AcceptButton2),cv.COLOR_RGB2BGR)

AcceptButton3Path = "AcceptButton1600x900.png"
AcceptButton3 = cv.imread(Path(AcceptButton3Path), 0)
AcceptButton3 = cv.cvtColor(np.array(AcceptButton3),cv.COLOR_RGB2BGR)

SearchBar1Path = "SearchBar1024x576.png"
SearchBar1 = cv.imread(Path(SearchBar1Path))
SearchBar1 = cv.cvtColor(np.array(SearchBar1),cv.COLOR_RGB2BGR)

SearchBar2Path = "SearchBar1280x720.png"
SearchBar2 = cv.imread(Path(SearchBar2Path))
SearchBar2 = cv.cvtColor(np.array(SearchBar2),cv.COLOR_RGB2BGR)

SearchBar3Path = "SearchBar1600x900.png"
SearchBar3 = cv.imread(Path(SearchBar3Path))
SearchBar3 = cv.cvtColor(np.array(SearchBar3),cv.COLOR_RGB2BGR)

BanButton1Path = "BanButton1024x576.png"
BanButton1 = cv.imread(Path(BanButton1Path))
BanButton1 = cv.cvtColor(np.array(BanButton1),cv.COLOR_RGB2BGR)

BanButton2Path = "BanButton1280x720.png"
BanButton2 = cv.imread(Path(BanButton2Path))
BanButton2 = cv.cvtColor(np.array(BanButton2),cv.COLOR_RGB2BGR)

BanButton3Path = "BanButton1600x900.png"
BanButton3 = cv.imread(Path(BanButton3Path))
BanButton3 = cv.cvtColor(np.array(BanButton3),cv.COLOR_RGB2BGR)

TopLane1Path = "TopLane1024x576.png"
TopLane1 = cv.imread(Path(TopLane1Path))
TopLane1 = cv.cvtColor(np.array(TopLane1),cv.COLOR_RGB2BGR)

TopLane2Path = "TopLane1280x720.png"
TopLane2 = cv.imread(Path(TopLane2Path))
TopLane2 = cv.cvtColor(np.array(TopLane2),cv.COLOR_RGB2BGR)

TopLane3Path = "TopLane1600x900.png"
TopLane3 = cv.imread(Path(TopLane3Path))
TopLane3 = cv.cvtColor(np.array(TopLane3),cv.COLOR_RGB2BGR)

InQueue1Path = "InQueue1024x576.png"
InQueue1 = cv.imread(Path(InQueue1Path))
InQueue1 = cv.cvtColor(np.array(InQueue1),cv.COLOR_RGB2BGR)

InQueue2Path = "InQueue1280x720.png"
InQueue2 = cv.imread(Path(InQueue2Path))
InQueue2 = cv.cvtColor(np.array(InQueue2),cv.COLOR_RGB2BGR)

InQueue3Path = "InQueue1600x900.png"
InQueue3 = cv.imread(Path(InQueue3Path))
InQueue3 = cv.cvtColor(np.array(InQueue3),cv.COLOR_RGB2BGR)

LockIn1Path = "LockIn1024x576.png"
LockIn1 = cv.imread(Path(LockIn1Path))
LockIn1 = cv.cvtColor(np.array(LockIn1),cv.COLOR_RGB2BGR)

LockIn2Path = "LockIn1280x720.png"
LockIn2 = cv.imread(Path(LockIn2Path))
LockIn2 = cv.cvtColor(np.array(LockIn2),cv.COLOR_RGB2BGR)

LockIn3Path = "LockIn1600x900.png"
LockIn3 = cv.imread(Path(LockIn3Path))
LockIn3 = cv.cvtColor(np.array(LockIn3),cv.COLOR_RGB2BGR)

DodgeCheck1Path = "DodgeCheck1024x576.png"
DodgeCheck1 = cv.imread(Path(DodgeCheck1Path))
DodgeCheck1 = cv.cvtColor(np.array(DodgeCheck1),cv.COLOR_RGB2BGR)

DodgeCheck2Path = "DodgeCheck1280x720.png"
DodgeCheck2 = cv.imread(Path(DodgeCheck2Path))
DodgeCheck2 = cv.cvtColor(np.array(DodgeCheck2),cv.COLOR_RGB2BGR)

DodgeCheck3Path = "DodgeCheck1600x900.png"
DodgeCheck3 = cv.imread(Path(DodgeCheck3Path))
DodgeCheck3 = cv.cvtColor(np.array(DodgeCheck3),cv.COLOR_RGB2BGR)


AcceptButtons = [AcceptButton1, AcceptButton2, AcceptButton3]
SearchBar = [SearchBar1, SearchBar2, SearchBar3]
BanButton = [BanButton1, BanButton2, BanButton3]
InQueue = [InQueue1, InQueue2, InQueue3]
LockInButton = [LockIn1, LockIn2, LockIn3]
DodgeChecks = [DodgeCheck1, DodgeCheck2, DodgeCheck3]
TopLane = [TopLane1, TopLane2, TopLane3]

ChampToBan = ""
ChampToSelect = ""

#GUI Stuff
Window = TK.Tk()

TempChampToBan = TK.StringVar()
TempChampToSelect = TK.StringVar()

Window.geometry("280x100")
Window.resizable(False,False)
Window.title("Accept Queue")

ToggleAcceptLabel = TK.Label(text= "Accept queues")
ToggleAcceptLabel.grid(row = 0, column = 0, sticky = TK.W, padx = 6)
ToggleAcceptButton = TK.Button(text="OFF", width=10, command=ToggleAccept)
ToggleAcceptButton.grid(row = 0, column = 1)

ToggleSelectLabel = TK.Label(text= "Auto select and ban")
ToggleSelectLabel.grid(row = 1, column = 0, sticky = TK.W, padx = 6)
ToggleSelectButton = TK.Button(text="OFF", width=10, command=ToggleAutoSelect)
ToggleSelectButton.grid(row = 1, column = 1)

ChampSelectLabel = TK.Label(text= "Champ to select")
ChampSelectLabel.grid(row = 2, column = 0, sticky = TK.W, padx = 6)
ChampSelectText = TK.Entry(Window,textvariable = TempChampToSelect)
ChampSelectText.grid(row = 2, column = 1)
TempChampToSelect.trace("w", lambda name, index, mode, TempChampToSelect=TempChampToSelect: UpdateChampToSelect(TempChampToSelect))

ChampBanLabel = TK.Label(text= "Champ to ban")
ChampBanLabel.grid(row = 3, column = 0, sticky = TK.W, padx = 6)
ChampBanText = TK.Entry(Window,textvariable = TempChampToBan)
TempChampToBan.trace("w", lambda name, index, mode, TempChampToBan=TempChampToBan: UpdateChampToBan(TempChampToBan))
ChampBanText.grid(row = 3, column = 1)

Window.columnconfigure([0,1], weight=1)
Window.rowconfigure([0,1,2,3], weight = 2)
Window.mainloop()











