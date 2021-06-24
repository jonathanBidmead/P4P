import cv2 as cv

# image = cv.imread('task_something_BPFs_overlaid_40L.png')

# cv.imshow('task_something_BPFs_overlaid_40L.png', image)

# cv.waitKey(0)

capture = cv.VideoCapture(0)
isTrue, newFrame = capture.read() # initialising match to ensure it is correct size
matchFrame = newFrame
while True:
    isTrue, frame = capture.read()
    #frame = cv.resize(frame, (1920,1080))
    frameEdges = cv.Canny(frame,120,200)
    
    cv.imshow('edges',frameEdges)

    if(cv.waitKey(20) & 0xFF==ord('d')):
        break

capture.release()
cv.destroyAllWindows
