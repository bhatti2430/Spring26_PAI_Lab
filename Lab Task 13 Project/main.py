import cv2
import cvzone
from rembg import remove
import os
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
cap.set(cv2.CAP_PROP_FPS, 60)

listImg = os.listdir("img")

imgList = []
for imgPath in listImg:
    img = cv2.imread(f'img/{imgPath}')
    img = cv2.resize(img, (640, 480))
    imgList.append(img)

indexImg = 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    imgOut = remove(img)
    alpha = imgOut[:, :, 3] / 255.0
    alpha = alpha[:, :, np.newaxis]
    imgOut = (imgOut[:, :, :3] * alpha + imgList[indexImg] * (1 - alpha)).astype(np.uint8)
    
    imgStacked = cvzone.stackImages([img, imgOut], 2, 1)

    cv2.imshow("Image", imgStacked)
    key = cv2.waitKey(1)
    if key == ord('a'):
        if indexImg>0:
            indexImg -= 1
    elif key == ord('d'):
        if indexImg<len(imgList)-1:
            indexImg += 1
    elif key == ord('q'):
        break