import cv2 as cv

capture = cv.VideoCapture(0)
tracker = cv.TrackerCSRT_create()
isTrue, initialFrame = capture.read()
bounds = cv.selectROI("Object To Track", initialFrame, False)
tracker.init(initialFrame, bounds)
print(bounds)
def drawBounds(frame, bounds):
    x,y,w,h = int(bounds[0]),int(bounds[1]),int(bounds[2]),int(bounds[3])
    cv.rectangle(frame, (x, y), ((x+w), (y+h)), (255,0,0) ,3 ,1)
    cv.putText(frame, "Tracking", (20,100), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0),2)

while True:
    timer = cv.getTickCount()
    success, frame = capture.read()
    success, bounds = tracker.update(frame)

    if success:
        drawBounds(frame,bounds)
    else:
        cv.putText(frame, "Failed", (20,200), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0),2)
    
    fps = cv.getTickFrequency()/(cv.getTickCount() - timer)
    cv.putText(frame, str(int(fps)), (20,300), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0),2)
    
    cv.imshow("feed", frame)


    if (cv.waitKey(20) & 0xFF==ord('d')):
        break
