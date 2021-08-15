import cv2
import numpy as np
import utils
from Calli import callibrate

img_counter = 0
webcam = True
path = "test2.png"
cap = cv2.VideoCapture(1)
cap.set(10,160)
cap.set(2,1920)
cap.set(4,1080)
scale = 1
wP = 400 * scale
hP = 400 * scale

# ret, mtx, dist, rvecs, tvecs = callibrate.cal()

while True:
    if webcam: success,img = cap.read()
    else: img = cv2.imread(path)

    cv2.imshow('Original',img) 


    # h,  w = img.shape[:2]
    # newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

    # # undistort
    # img = cv2.undistort(img, mtx, dist, None, newcameramtx)
    # # crop the image
    # x, y, w, h = roi
    # img = img[y:y+h, x:x+w]
    
    # cv2.imshow('Undistored',img)
    
    imgContours, conts = utils.getContours(img,showCanny=False,minArea=20000,filter=4,draw = True)
    # cv2.imshow('Detected',imgContours)
    

    if len(conts) != 0:
        biggest = conts[0][2]
        imgWarp = utils.warpImg(img,biggest,wP,hP)
        imgContours2, conts2, x,y = utils.circleContour(imgWarp,cThr = [100,100],showCanny=False,minArea=1000,filter=0,draw = True)
        cv2.imshow('Wraped Contours',imgContours2)


    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "bb{}.png".format(img_counter)
        cv2.imwrite(img_name, img)
        print("{} written!".format(img_name))
        img_counter += 1
    

cap.release()

cv2.destroyAllWindows()

