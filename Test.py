import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import pyautogui
import time
import imutils

#Returns screenshot of screen
def Screenshot():
    Screen = pyautogui.screenshot()
    Screen = cv.cvtColor(np.array(Screen), cv.COLOR_BGR2GRAY)
    return Screen

#Compare screenshot to passed image template as argument
def TemplateMatch(Template):

    #Take a screenshot
    Screen = Screenshot()
    found = None
    #loop over scaled versions of screenshot
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        #Resize image
        Resized = imutils.resize(Screen, width = int(Screen.shape[1] * scale))
        r = Screen.shape[1] / float(Resized.shape[1])
        #Make sure scaled image is bigger than template
        if Resized.shape[0] < tH or Resized.shape[1] < tW:
            break
        #Edge template image
        edged = cv.Canny(Resized, 50, 200)
        #Comapre images using OPENCV
        Result = cv.matchTemplate(edged, Template, cv.TM_CCOEFF_NORMED)
        #Grab maxVal and compare it until best match is obtained
        (_, maxVal, _, maxLoc) = cv.minMaxLoc(Result)
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)  
    #Show image with selection
    (_, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
    cv.rectangle(Screen, (startX, startY), (endX, endY), (0, 0, 255), 2)
    cv.imshow("Image", Screen)
    cv.waitKey(0)

time.sleep(3)
Template = cv.imread('Images/AcceptButton.png', 0)
Template = cv.Canny(Template, 50, 200)
(tH, tW) =Template.shape[:2]
TemplateMatch(Template)