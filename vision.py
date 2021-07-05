import cv2 as cv
import numpy as np

cap = cv.VideoCapture(1)

while True:
    _,frame = cap.read()
    cv.imshow("Frame",frame)
    key = cv.waitKey(1)
    if key == 27:
        break

cap.release()