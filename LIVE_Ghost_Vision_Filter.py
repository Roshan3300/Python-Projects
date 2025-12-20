import cv2
import numpy as numpy

cam=cv2.VideoCapture(0)

while True:
    ret, frame=cam.read()
    grey=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur=cv2.bitwise_not(grey)
    blur=cv2.GaussianBlur(blur,(21,21),0)
    ghost=cv2.divide(grey, 255-blur, scale=256)
    
    cv2.imshow("👻 BHUUUT 👻", ghost)
    if cv2.waitKey(1) & 0xFF == 27:
        break
    
cam.release()
cv2.destroyAllWindows()