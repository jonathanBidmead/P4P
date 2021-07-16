import numpy as np
import cv2 as cv



def cal():
    chessboardsize = (9,6)

    # termination criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((chessboardsize[0]*chessboardsize[1],3), np.float32)
    objp[:,:2] = np.mgrid[0:chessboardsize[0],0:chessboardsize[1]].T.reshape(-1,2)
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    counter = 0



    while counter < 8:
        # print()
        # success,img = cap.read()
        img = cv.imread("Calli/test{}.png".format(counter))
        # cv.imshow("aa",img)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)


        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(img, chessboardsize, None)
        # If found, add object points, image points (after refining them)
        print(ret)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners)
            # Draw and display the corners
            cv.drawChessboardCorners(img, chessboardsize, corners2, ret)
            cv.imshow('img', img)
            # cv.waitKey(0)
        
        counter = counter + 1
    # k = cv.waitKey(1)
    # if k%256 == 27:
    #     # ESC pressed
    #     print("Escape hit, closing...")
    #     break



    cv.destroyAllWindows()

    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    return ret,mtx,dist,rvecs,tvecs

# print("ret: ")
# print(ret)
# print(" ")
# print("mtx")
# print(mtx)
# print("")
# print("dist")
# print(dist)
# print("")
# print("rvecs")
# print(rvecs)
# print("")
# print("tvecs")
# print(tvecs)


# img = cv.imread('parttest.png')
# h,  w = img.shape[:2]
# newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

# # undistort
# dst = cv.undistort(img, mtx, dist, None, newcameramtx)
# # crop the image
# x, y, w, h = roi
# dst = dst[y:y+h, x:x+w]
# cv.imshow("dst",dst)
# cv.waitKey(0)


# cv.destroyAllWindows()