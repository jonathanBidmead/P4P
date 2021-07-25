from typing import final
import math
import cv2 
import numpy as np
from numpy.core.fromnumeric import argmax

def circleContour(img,cThr=[100,100],showCanny=False,minArea = 1000,filter = 0,draw = False):
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
    imgCanny = cv2.Canny(imgBlur,cThr[0],cThr[1])
    kernel = np.ones((5,5))
    imgDial= cv2.dilate(imgCanny,kernel,iterations=1)
    imgThre = cv2.erode(imgDial,kernel,iterations=1)

    if showCanny: cv2.imshow('Canny',imgThre)

    contours,hiearchy = cv2.findContours(imgThre,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)


    finalContours = []
    for i in contours:
        area = cv2.contourArea(i)
        if area > minArea:
            peri = cv2.arcLength(i,True)
            approx = cv2.approxPolyDP(i,0.02*peri,True)
            bbox = cv2.boundingRect(approx)

            if filter > 0:
                if len(approx) == filter:
                    finalContours.append([len(approx),area,approx,bbox,i])
            
            else:
                finalContours.append([len(approx),area,approx,bbox,i])
    
        
    finalContours = sorted(finalContours,key = lambda x:x[1],reverse = False)

    # con = finalContours[2]
    # print(con[4])
    # cv2.drawContours(img, con[4], -1, (0,255,0), 3)
    # print(len(contours))

    con = finalContours[0]
       
    if(len(finalContours)):
        if draw:
            # cv2.drawContours(img,con[4],-1,(0,0,255),3)
            centres, radius = cv2.minEnclosingCircle(con[4])
            x = int(centres[0])
            y = int(centres[1])

            if(len(finalContours) > 2):
                row,_,col = finalContours[-1][4].shape
                con_r = finalContours[-1][4].reshape(row,col)
                filter_arr = []
                diff = 1000
                centre_fin = 0
                radius_fin = 0


                for thresh in range(30,100):
                    for i in con_r:
                        if(abs(x-i[0]) + abs(y-i[1]) > thresh):
                            filter_arr.append(True)
                        else:
                            filter_arr.append(False)

                    filtered_con = con_r[filter_arr]
                    row,col = filtered_con.shape 
                    filtered_con = filtered_con.reshape(row,1,col)


                    centres_fil, radius_fil = cv2.minEnclosingCircle(filtered_con)
                    if(abs(radius_fil - radius) < diff):
                        diff = abs(radius_fil - radius) 
                        centre_fin = centres_fil
                        radius_fin = radius_fil
                    
                    filter_arr = []


                x = int(centre_fin[0])
                y = int(centre_fin[1])
                radius = radius_fin

    cv2.circle(img,(x,y),int(radius),(0,0,255),2)
    distance = math.sqrt((x**2 + y**2))
    cv2.putText(img, "X: " + str(x) + "  Y:" + str(y), (x+30, y+30),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    print("x" + str(x))
    print("y" + str(y))

    print("-----------")
    #         cv2.putText(img, "Distance: " + str(distance), (x - 50, y - 60),
    # cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    #         cv2.putText(img, "Radius: " + str(int(radius)), (x - 50, y - 80),
    # cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    return img,finalContours


def getContours(img,cThr=[100,100],showCanny=False,minArea = 10000,filter = 0,draw = False):
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
    imgCanny = cv2.Canny(imgBlur,cThr[0],cThr[1])
    kernel = np.ones((5,5))
    imgDial= cv2.dilate(imgCanny,kernel,iterations=1)
    imgThre = cv2.erode(imgDial,kernel,iterations=1)

    if showCanny: cv2.imshow('Canny',imgThre)

    contours,hiearchy = cv2.findContours(imgThre,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    finalContours = []
    for i in contours:
        area = cv2.contourArea(i)
        if area > minArea:
            peri = cv2.arcLength(i,True)
            approx = cv2.approxPolyDP(i,0.02*peri,True)
            bbox = cv2.boundingRect(approx)

            if filter > 0:
                if len(approx) == filter:
                    finalContours.append([len(approx),area,approx,bbox,i])
            
            else:
                finalContours.append([len(approx),area,approx,bbox,i])
        
    finalContours = sorted(finalContours,key = lambda x:x[1],reverse = True)

    if draw:
        for con in finalContours:
            cv2.drawContours(img,con[4],-1,(0,0,255),3)

    return img,finalContours

def reorder(myPoints):
    myPointsNew = np.zeros_like(myPoints)
    myPoints = myPoints.reshape((4,2))
    add = myPoints.sum(1) 
    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] = myPoints[np.argmax(add)]
    diff = np.diff(myPoints,axis = 1)
    myPointsNew[1] = myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]
    
    return myPointsNew



def warpImg(img,points,w,h,pad = 3):
    points = reorder(points)
    pts1 = np.float32(points)
    pts2 = np.float32([[0,0],[w,0],[0,h],[w,h]])
    matrix = cv2.getPerspectiveTransform(pts1,pts2)
    imgWarp = cv2.warpPerspective(img,matrix,(w,h))

    imgWarp = imgWarp[pad:imgWarp.shape[0]-pad,pad:imgWarp.shape[1]-pad]

    return imgWarp

