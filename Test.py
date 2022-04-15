import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import pyautogui
import time

def Screenshot():
    Screen = pyautogui.screenshot()
    Screen = cv.cvtColor(np.array(Screen), cv.COLOR_BGR2GRAY)
    return Screen

def TemplateMatch(Template):
    Screen = Screenshot()
    Result = cv.matchTemplate(Template,Screen,cv.TM_CCOEFF_NORMED)
    (minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(Result)
    (startX, startY) = maxLoc
    endX = startX + Template.shape[1]
    endY = startY + Template.shape[0]
    ResultImage = None
    cv.rectangle(ResultImage, (startX, startY), (endX, endY), (255, 0, 0), 3)
    # show the output image
    cv.imshow("Output", ResultImage)
    cv.waitKey(0)

time.sleep(3)
Template = cv.imread('Images/AcceptButton.jpg',0)
TemplateMatch(Template)