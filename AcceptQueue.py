from ttkwidgets.autocomplete import AutocompleteEntry
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
import urllib.request, json 

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

#Move mouse and click 
def Click(X, Y, Height, Width, Clicks):
    X = int((X + (Width/2)))
    Y = int((Y + (Height/2)))
    pyautogui.click(x = X, y= Y,clicks=Clicks)  

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
            Click(maxLoc[0], maxLoc[1], TemplateHeight, TemplateWidth, 1)
            time.sleep(4)
        time.sleep(2)

#Champ select process    
def ChampSelect():
    global ChampToSelect, InChampSelect, ChampToBan, AlternativeChampToSelect, LockInButton
    SearchBarLoc = list()
    maxVal, SearchBarHeight,SearchBarWidth = 0, 0, 0
    if InChampSelect:
        while maxVal < 0.75 and InChampSelect and AutoSelect:
            maxVal, _, _, _ = TemplateMatch(BanButton, True)
            time.sleep(2)
        maxVal = 0
        if InChampSelect:
            BanChamp(ChampToBan)
        while maxVal < 0.75 and InChampSelect and AutoSelect:
            maxVal, SearchBarLoc, SearchBarHeight, SearchBarWidth = TemplateMatch(SearchBar, False)
            time.sleep(2)
        if InChampSelect and AutoSelect:
            SearchForChamp(ChampToSelect)
            time.sleep(0.1)
            SelectChamp()
            time.sleep(0.2)
            LockInChamp()
            time.sleep(0.2)
            maxVal, _ ,_ ,_  = TemplateMatch(LockInButton, True)
            if maxVal >= 0.75:
                SearchForAlternativeChamp(AlternativeChampToSelect,SearchBarLoc[0], SearchBarLoc[1],SearchBarHeight, SearchBarWidth)
                time.sleep(0.1)
                SelectChamp()
                time.sleep(0.1)
                LockInChamp()

#Click on lock in button
def LockInChamp():
    global LockIn
    maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(LockInButton, True)
    if maxVal > 0.75 and AutoSelect:
        Click(maxLoc[0], maxLoc[1], TemplateHeight, TemplateWidth, 1)

#Search for champ and select it then click ban button
def BanChamp(ChampToBan):

    global BanButton
    SearchForChamp(ChampToBan)
    time.sleep(0.1)
    SelectChamp()
    maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(BanButton, True)
    if maxVal >= 0.75 and AutoSelect:
        Click(maxLoc[0], maxLoc[1], TemplateHeight, TemplateWidth, 1)
    return maxVal
    

#Searches for champ and clicks it using Click()
def SearchForChamp(ChampName):

    global SearchBar1
    maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(SearchBar, False)
    if maxVal > 0.75 and AutoSelect:   
         Click(maxLoc[0], maxLoc[1], TemplateHeight, TemplateWidth, 1)
         pyautogui.write(ChampName)
    return maxVal

#Clears searchbar and searches for champ and clicks it using Click()
def SearchForAlternativeChamp(ChampName, X, Y, TemplateHeight, TemplateWidth):
    Click(X, Y, TemplateHeight, TemplateWidth, 2)
    pyautogui.write(ChampName) 

#Selects champ that was searched for
def SelectChamp():
    global TopLane
    maxVal, maxLoc, TemplateHeight, TemplateWidth = TemplateMatch(TopLane, False)
    if maxVal >= 0.75:
        Click(maxLoc[0] + 25 , maxLoc[1] + 50, TemplateHeight, TemplateWidth, 1)
    return maxVal
    
#After entering champ select check if it is dodged and update InChamoSelect
def DodgeCheck():
    global InChampSelect, DodgeChecks, AutoSelect
    while True and AutoSelect:
        while InChampSelect and AutoSelect:
            maxVal, _, _, _ = TemplateMatch(DodgeChecks, True)
            if maxVal >= 0.75:
                InChampSelect = False
            time.sleep(5)
        time.sleep(5)

#Check if in champ select then run ChampSelect() on different Thread
def CheckChampSelect():
    global SearchBar1, InChampSelect, AutoSelect

    while True and AutoSelect:
        while  AutoSelect and not InChampSelect :
            maxVal, _, _, _ = TemplateMatch(SearchBar, False)
            if maxVal >= 0.75:
                InChampSelect = True
                ChampSelectThread = Thread(target = ChampSelect, daemon = True)
                ChampSelectThread.start()
                ChampSelectThread.join(timeout = 150)
                InChampSelect = False
            if not InChampSelect:
                time.sleep(5)


#Initiate required methods for auto champ select ond ifferent threads
InChampSelect = False
def Procedure():
    CheckChampSelectThread = Thread(target = CheckChampSelect, daemon = True)
    DodgeCheckThread = Thread(target= DodgeCheck, daemon = True)
    CheckChampSelectThread.start()
    DodgeCheckThread.start()


#Toggle auto champ select and run Prcoedure() on different thread
AutoSelect = False
def ToggleAutoSelect():
    global AutoSelect, ToggleSelectButton, ChampBanText, ChampSelectText, AlternativeChampSelectText, ChampToSelect, AlternativeChampToSelect, ChampToBan
    ProcedureThread = Thread(target = Procedure, daemon= True)

    if AutoSelect:
        ToggleSelectButton.config(text='OFF')
        ChampSelectText.config(state = TK.NORMAL)
        AlternativeChampSelectText.config(state = TK.NORMAL)
        ChampBanText.config(state = TK.NORMAL)
        AutoSelect = False
        
    else:
        ToggleSelectButton.config(text='ON')
        ChampSelectText.config(state = TK.DISABLED)
        AlternativeChampSelectText.config(state = TK.DISABLED)
        ChampBanText.config(state = TK.DISABLED)
        ChampToSelect, AlternativeChampToSelect, ChampToBan = ChampSelectText.get(), AlternativeChampSelectText.get(), ChampBanText.get()
        AutoSelect = True
        ProcedureThread.start()

#Toggle auto accept  and run AcceptQueue() on different thread      
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

################################################################ Assets

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

################################################################ Assets

ChampToBan = ""
ChampToSelect = ""
AlternativeChampToSelect = ""

#Champ list for autocomplete
with urllib.request.urlopen("http://ddragon.leagueoflegends.com/cdn/12.12.1/data/en_US/champion.json") as url:
    data = json.loads(url.read().decode())
    Champs = []
    for Champ in data["data"]:
        Champs.append(Champ)

#GUI Stuff
Window = TK.Tk()
Window.geometry("300x150")
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
ChampSelectText = AutocompleteEntry(completevalues=Champs)
ChampSelectText.grid(row = 2, column = 1)

AlternativeChampSelectLabel = TK.Label(text= "Alternative champ to select")
AlternativeChampSelectLabel.grid(row = 3, column = 0, sticky = TK.W, padx = 6)
AlternativeChampSelectText = AutocompleteEntry(completevalues=Champs)
AlternativeChampSelectText.grid(row = 3, column = 1)

ChampBanLabel = TK.Label(text= "Champ to ban")
ChampBanLabel.grid(row = 4, column = 0, sticky = TK.W, padx = 6)
ChampBanText = AutocompleteEntry(completevalues=Champs)
ChampBanText.grid(row = 4, column = 1)

Window.columnconfigure([0,1], weight=2)
Window.rowconfigure([0,1,2,3,4], weight = 2)
Window.mainloop()











