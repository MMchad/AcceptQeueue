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
    W, H = Template.shape[::-1]
    Result = cv.matchTemplate(Template, Screen,cv.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where( Result >= threshold)
    (minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(Result)
    print(maxVal)
    Top_Left = maxLoc
    Bottom_Right = (Top_Left[0] + W, Top_Left[1] + H)
    cv.rectangle(Screen,Top_Left, Bottom_Right, 255, 2)
    plt.subplot(121),plt.imshow(Result,cmap = 'gray')
    plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(Screen,cmap = 'gray')
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.show()

time.sleep(3)
Template = cv.imread('Images/AcceptButton.jpg', 0)
TemplateMatch(Template)